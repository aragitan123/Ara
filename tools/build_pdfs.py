#!/usr/bin/env python3
"""검단아라학원 12월 겨울방학 특강 연습 학습지 4종 생성기.

    python3 tools/build_pdfs.py            # 4종 모두
    python3 tools/build_pdfs.py 1          # 01번만
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (CondPageBreak, KeepTogether, PageBreak,
                                Paragraph, Spacer)

import pdfkit as K
from pdfkit import (CORAL, CORAL_LINE, CREAM, CREAM_DEEP, GRAY, INK, LINE,
                    MINT, MINT_SOFT, NAVY, NAVY_SOFT, P, S)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "downloads")
os.makedirs(OUT, exist_ok=True)

CW = K.CONTENT_W


# ------------------------------------------------------------------ helpers ---
def gap(h=6):
    return Spacer(1, h)


def tip(text, title="풀이 팁"):
    return K.box([Paragraph("<font color='#3F7D6B'><b>%s</b></font>  %s" % (title, text),
                            S(fontSize=9, leading=15, textColor=INK))],
                 bg=MINT_SOFT, border=colors.HexColor("#BFD9CE"), pad=8)


def expr_line(ratio=(0.58, 0.42), height=24, label_w=10 * mm, color="#C9BCAF"):
    """식 / 답 write-in line pair."""
    rest = CW - label_w * 2 - 12
    lw, rw = rest * ratio[0], rest * ratio[1]
    t = K.Table([[Paragraph("식", S(fontSize=9.2, leading=14, textColor=CORAL)), "",
                  Paragraph("답", S(fontSize=9.2, leading=14, textColor=CORAL)), ""]],
                colWidths=[label_w, lw, label_w, rw], rowHeights=[height])
    t.setStyle(K.TableStyle([
        ("LINEBELOW", (1, 0), (1, 0), 0.7, colors.HexColor(color)),
        ("LINEBELOW", (3, 0), (3, 0), 0.7, colors.HexColor(color)),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return t


def intro_line(text, label="풀이", height=26, label_w=10 * mm):
    """One wide write-in line with a label."""
    t = K.Table([[Paragraph(label, S(fontSize=9.2, leading=14, textColor=CORAL)),
                  Paragraph(text, S(fontSize=9, leading=14, textColor=GRAY)), ""]],
                colWidths=[label_w, CW * 0.42, CW - label_w - CW * 0.42], rowHeights=[height])
    t.setStyle(K.TableStyle([
        ("LINEBELOW", (2, 0), (2, 0), 0.7, colors.HexColor("#C9BCAF")),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return t


def trace_grid(chars, cells=5, cell_h=30):
    """따라 쓰기 격자: 한 글자 + 빈 칸."""
    rows = []
    for ch, reading in chars:
        row = [Paragraph("<font name='KRS' size='15'>%s</font>" % ch,
                         S(fontSize=11, leading=15)),
               Paragraph(reading, S(fontSize=8.4, leading=13, textColor=GRAY))]
        row += [""] * cells
        rows.append(row)
    widths = [11 * mm, 17 * mm] + [(CW - 28 * mm) / cells] * cells
    return K.table(rows, widths, header=False, row_h=cell_h,
                   body_style=[("ALIGN", (0, 0), (1, -1), "CENTER")])


def note(text, title="알아 두기"):
    return K.box([Paragraph("<font color='#DE5B3C'><b>%s</b></font>  %s" % (title, text),
                            S(fontSize=9, leading=15, textColor=INK))],
                 bg=CREAM, border=CORAL_LINE, pad=8)


def answer_block(lines):
    out = list(K.section("答", "정답과 풀이", "먼저 스스로 풀어 본 뒤에 확인해 보세요."))
    for head, body in lines:
        out.append(Paragraph(head, S(fontName="KRB", fontSize=9.6, leading=14, textColor=CORAL)))
        out.append(gap(1))
        out.append(Paragraph(body, S(fontSize=9, leading=14.5)))
        out.append(gap(5))
    return out


def numgrid(row_labels, data, col_w=None, cell_h=22, label_w=20 * mm, font=9.6):
    """Row-label table: label + data cells (all centred)."""
    ncols = max(len(r) for r in data)
    cw = col_w or (CW - label_w) / ncols
    rows = []
    for lab, row in zip(row_labels, data):
        rows.append([Paragraph("<b>%s</b>" % lab, S(fontSize=9.2, leading=13, textColor=NAVY))] +
                    [Paragraph(str(v), S(fontSize=font, leading=13)) if v != "" else "" for v in row])
    t = K.table(rows, [label_w] + [cw] * ncols, header=False, row_h=cell_h,
                body_style=[("BACKGROUND", (0, 0), (0, -1), CREAM_DEEP)])
    return t


def cells(rows_text, ncols, cell_h=22, label_w=20 * mm, head=True, first_col_bg=True):
    """Plain grid where every cell is text (used for fill-in tables)."""
    first_col_bg = first_col_bg and bool(label_w)
    label_w_ = label_w if first_col_bg else 0
    cw = (CW - label_w_) / ncols
    data = []
    for r, row in enumerate(rows_text):
        line = []
        for c, cell in enumerate(row):
            if isinstance(cell, str):
                line.append(Paragraph(cell, S(fontSize=9.4, leading=13,
                                              textColor=NAVY if (head and r == 0) else INK)))
            else:
                line.append(cell)
        data.append(line)
    widths = ([label_w_] if first_col_bg else []) + [cw if first_col_bg else (CW / ncols)] * ncols
    style = []
    if head:
        style += [("BACKGROUND", (1 if first_col_bg else 0, 0), (-1, 0), NAVY_SOFT)]
    if first_col_bg:
        style += [("BACKGROUND", (0, 0), (0, -1), CREAM_DEEP)]
    t = K.table(data, widths, header=False, row_h=cell_h, body_style=style)
    return t


def two_col(left, right, ratio=0.5, pad=8, total=None):
    """Place two flowable lists side by side."""
    total = total or (CW - 30)
    lw = (total - pad) * ratio
    rw = total - pad - lw
    t = K.Table([[left, "", right]], colWidths=[lw, pad, rw])
    t.setStyle(K.TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def calc_box(items, cols=3, cell_h=46, font=12):
    """Small calculation cards: '13 + 5 = ____'."""
    rows, row = [], []
    for i, it in enumerate(items, 1):
        row.append(Paragraph("<font color='#B0A69C'>%d</font>&nbsp;&nbsp;%s" % (i, it),
                             S(fontSize=font, leading=18)))
        if len(row) == cols:
            rows.append(row)
            row = []
    if row:
        row += [""] * (cols - len(row))
        rows.append(row)
    cw = CW / cols
    t = K.table(rows, [cw] * cols, header=False, row_h=cell_h,
                body_style=[("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER")])
    return t


class VerticalCalcs(K.Flowable):
    """세로셈 칸: numbers stacked with an operator and a result line."""

    def __init__(self, items, cell_h=86, digit_w=17):
        self.items = items          # [(27, "+", 15), ...]
        self.cell_h = cell_h
        self.digit_w = digit_w
        self.height = cell_h

    def wrap(self, aw, ah):
        self.w = aw
        self.cell_w = aw / len(self.items)
        return self.w, self.height

    def draw(self):
        C = self.canv
        C.saveState()
        for i, (a, op, b) in enumerate(self.items):
            x0 = i * self.cell_w
            C.setStrokeColor(K.LINE)
            C.setLineWidth(0.7)
            C.rect(x0, 0, self.cell_w, self.cell_h, stroke=1, fill=0)
            digits = max(len(str(a)), len(str(b)))
            right = x0 + self.cell_w - 16
            top = self.cell_h - 22
            C.setFont("KR", 17)
            C.setFillColor(K.INK)
            # first number
            for k, ch in enumerate(str(a)[::-1]):
                C.drawRightString(right - k * self.digit_w, top, ch)
            # operator + second number
            for k, ch in enumerate(str(b)[::-1]):
                C.drawRightString(right - k * self.digit_w, top - 24, ch)
            C.setFont("KRB", 15)
            C.setFillColor(K.CORAL)
            C.drawRightString(right - (digits - 0.35) * self.digit_w - 4, top - 24, op)
            C.setStrokeColor(K.NAVY)
            C.setLineWidth(1.3)
            C.line(right - digits * self.digit_w - 6, top - 30, right + 6, top - 30)
        C.restoreState()


def vertical_box(items, cell_h=86):
    return VerticalCalcs(items, cell_h=cell_h)


# ============================================================== 학습지 01 ====
def pdf_01():
    meta = dict(
        title="50 이하 수, 두 가지로 읽고<br/>여러 가지로 계산하기",
        title_plain="01 초1 덧뺄셈·50 이하 두 가지 읽기",
        short_title="01 덧셈·뺄셈과 두 가지 읽기",
        tag="12월 겨울방학 특강 · 예비초1 · 초등 1학년",
        sub="일·이·삼으로 읽기 / 하나·둘·셋으로 읽기, 그리고 여러 가지 덧셈·뺄셈",
        intro="같은 수를 두 가지 이름으로 읽을 수 있으면, 문제에 나오는 수를 훨씬 편하게 붙잡을 수 있습니다. "
              "이 학습지는 50 이하의 수를 두 가지로 읽는 연습에서 시작해, 가르기와 모으기, 여러 가지 덧셈·뺄셈, "
              "그리고 유형을 한눈에 알아보는 풀이법까지 한 번에 이어지도록 만들었습니다.",
        goals=[
            "1~50의 수를 한자어(일·이·삼)와 고유어(하나·둘·셋)로 읽고 쓸 수 있어요.",
            "10 만들기와 가르기·모으기로 계산의 바탕을 세워요.",
            "받아올림·받아내림이 있는 덧셈과 뺄셈을 여러 가지로 연습해요.",
            "문제의 유형을 알아보고 식을 세우는 방법을 익혀요.",
        ],
        steps=["50 이하 수 두 가지로 읽기", "10 만들기와 가르기·모으기",
               "여러 가지 덧셈과 뺄셈", "한눈에 보는 유형 풀이법", "정답과 풀이"],
    )

    st = []

    # ---------------- page: 01 두 가지 읽기 ----------------
    st += K.section("01", "50 이하 수, 두 가지로 읽기", "같은 수를 두 가지 이름으로 읽어 봅니다.")
    st.append(P("<b>한자어 읽기</b>는 일·이·삼처럼, <b>고유어 읽기</b>는 하나·둘·셋처럼 읽는 방법입니다. "
                "수를 셀 때는 고유어를, 날짜·차례에는 한자어를 주로 씁니다.", "body_j"))
    st.append(gap(8))
    st.append(numgrid(
        ["수", "한자어 읽기", "고유어 읽기"],
        [["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
         ["일", "이", "삼", "사", "오", "육", "칠", "팔", "구", "십"],
         ["하나", "둘", "셋", "넷", "다섯", "여섯", "일곱", "여덟", "아홉", "열"]],
        cell_h=22))
    st.append(gap(5))
    st.append(Paragraph("※ 1~10의 고유어는 '하나·둘·셋'이지만, 물건을 셀 때는 '한 개·두 개·세 개'로 모양이 바뀝니다. "
                        "(한 사람·두 사람, 한 살·두 살)", S(fontSize=8.6, leading=13, textColor=GRAY)))
    st.append(gap(11))

    st.append(K.problem("1", "11부터 20까지의 수를 두 가지로 읽어 표를 채워 보세요."))
    st.append(cells(
        [["수"] + ["11", "12", "13", "14", "15", "16", "17", "18", "19", "20"],
         ["한자어"] + [""] * 10,
         ["고유어"] + [""] * 10],
        ncols=10, cell_h=24, label_w=18 * mm))
    st.append(gap(12))

    st.append(K.problem("2", "다음 수를 한자어와 고유어, 두 가지로 써 보세요."))
    st.append(cells(
        [["수", "23", "35", "42", "27", "50"],
         ["한자어", "", "", "", "", ""],
         ["고유어", "", "", "", "", ""]],
        ncols=5, cell_h=26, label_w=18 * mm))
    st.append(gap(12))

    st.append(K.problem("3", "고유어로 읽은 수와 같은 수를 골라 선으로 이어 보세요."))
    st.append(K.ConnectCols(
        ["스물하나", "서른여덟", "마흔둘", "쉰", "열다섯", "이십구"],
        ["15", "21", "29", "38", "42", "50"], row_h=23))
    st.append(gap(8))
    st.append(tip("고유어 읽기는 '스물·서른·마흔·쉰'처럼 열 단위 이름을 먼저 익히면 빨라집니다. "
                  "20 스물, 30 서른, 40 마흔, 50 쉰 — 한자어로는 이십·삼십·사십·오십입니다."))
    st.append(gap(12))

    st.append(K.problem("4", "수를 두 가지로 읽는 힘을 기르는 수수께끼입니다. □ 안에 알맞은 수를 써 보세요."))
    for line in ["· 나는 스물보다 3 큰 수입니다. 나는 (      )입니다.",
                 "· 나는 서른보다 5 작은 수입니다. 나는 (      )입니다.",
                 "· 나는 마흔보다 2 큰 수입니다. 한자어로 '사십이'라고 읽습니다. 나는 (      )입니다."]:
        st.append(Paragraph(line, S(fontSize=9.6, leading=19)))
    st.append(PageBreak())

    # ---------------- page: 02 가르기·모으기 ----------------
    st += K.section("02", "10 만들기와 가르기·모으기", "계산의 바탕이 되는 힘을 먼저 세웁니다.")
    st.append(P("10이 되는 두 수를 바로 찾을 수 있으면, 받아올림과 받아내림이 훨씬 쉬워집니다. "
                "가르기는 하나의 수를 둘로 나누는 것, 모으기는 둘을 하나로 합치는 것입니다.", "body_j"))
    st.append(gap(9))

    st.append(K.problem("5", "더해서 10이 되는 수를 □ 안에 써 보세요."))
    st.append(calc_box(["7 + □", "□ + 4", "9 + □", "6 + □", "8 + □", "3 + □"], cols=6, cell_h=44))
    st.append(gap(12))

    st.append(K.problem("6", "□ 안에 알맞은 수를 써 보세요."))
    st.append(calc_box(["13 = 10 + □", "18 = 10 + □", "10 + 5 = □", "16 = □ + 6",
                        "17 = □ + 7", "10 + 10 = □", "□ = 10 + 9", "20 = 10 + □",
                        "25 + □ = 50", "38 + □ = 50", "47 + □ = 50", "19 + □ = 50"],
                       cols=4, cell_h=40))
    st.append(gap(10))

    st.append(K.problem("7", "두 수의 크기를 비교해 ○ 안에 >, <, = 를 써 보세요."))
    st.append(calc_box(["34 ○ 43", "27 ○ 27", "19 ○ 21", "40 ○ 39", "50 ○ 45", "12 ○ 21"],
                       cols=3, cell_h=42))
    st.append(gap(10))

    st.append(K.problem("8", "다음 수를 차례대로 써 보세요."))
    st.append(cells([["24", "", "", "", "", "", "", "", "", "33"]], ncols=10, cell_h=30,
                    label_w=0, head=False))
    st.append(gap(4))
    st.append(Paragraph("가운데 빈 곳에는 25부터 32까지가 들어갑니다. 천천히 하나씩 써 보세요.",
                        S(fontSize=8.4, leading=12, textColor=GRAY)))
    st.append(gap(12))

    st.append(K.problem("9", "생활 속에서 수를 바르게 읽어 보세요. 언제 한자어를 쓰고 언제 고유어를 쓰는지 생각해 보세요."))
    for line in ["· 우리 집은 아파트 (        )층에 있습니다.  → 층수는 ( 한자어 / 고유어 )로 읽습니다.",
                 "· 그릇에 사과가 (        )개 담겨 있습니다.  → 개수는 ( 한자어 / 고유어 )로 읽습니다.",
                 "· 오늘은 (        )월 (        )일입니다.  → 날짜는 ( 한자어 / 고유어 )로 읽습니다."]:
        st.append(Paragraph(line, S(fontSize=9.6, leading=19)))
    st.append(gap(8))
    st.append(tip("셀 때는 고유어(세 명), 차례·날짜·층수는 한자어(삼 층·십육 일)를 씁니다."))
    st.append(note("크기를 비교할 때는 <b>십의 자리</b>부터 봅니다. 십의 자리 수가 같으면 일의 자리 수를 봅니다. "
                   "예) 34와 43 → 십의 자리 3과 4를 비교해 34 < 43"))
    st.append(PageBreak())

    # ---------------- page: 03 여러 가지 계산 ----------------
    st += K.section("03", "여러 가지 덧셈과 뺄셈", "같은 계산을 여러 모양으로 만나 봅니다.")

    st.append(K.problem("10", "받아올림이 없는 덧셈입니다. 계산해 보세요."))
    st.append(calc_box(["13 + 5", "21 + 7", "34 + 3", "40 + 9", "12 + 12", "20 + 13"], cols=3, cell_h=46))
    st.append(gap(10))

    st.append(K.problem("11", "받아내림이 있는 뺄셈입니다. 계산해 보세요."))
    st.append(calc_box(["15 - 7", "23 - 9", "31 - 6", "42 - 8", "50 - 24", "18 - 9"], cols=3, cell_h=46))
    st.append(gap(5))
    st.append(tip("받아내림이 있는 뺄셈은 십의 자리에서 10을 하나 빌려와 계산합니다. "
                  "예) 23-9 → 13-9=4, 남은 십 1 → 14"))
    st.append(gap(10))

    st.append(K.problem("12", "세로셈으로 계산해 보세요."))
    st.append(vertical_box([(27, "+", 15), (43, "-", 18), (36, "+", 9)]))
    st.append(gap(10))

    st.append(K.problem("13", "세 수를 차례대로 계산해 보세요."))
    st.append(calc_box(["6 + 7 - 4", "15 - 8 + 3", "9 + 8 - 10", "20 - 6 + 5"], cols=2, cell_h=46))
    st.append(gap(10))

    st.append(K.problem("14", "□ 안에 알맞은 수를 써 보세요."))
    st.append(calc_box(["□ + 7 = 15", "14 - □ = 6", "□ - 8 = 9", "8 + □ = 17", "20 - □ = 11", "□ + 13 = 21"],
                       cols=3, cell_h=46))
    st.append(gap(10))

    st.append(PageBreak())

    # ---------------- page: 04 유형 풀이법 ----------------
    st += K.section("04", "한눈에 보는 유형 풀이법", "문제를 읽고 어떤 계산인지 먼저 알아봅니다.")

    rows = [[Paragraph("<b>유형</b>", S(fontSize=9, leading=12, textColor=colors.white)),
             Paragraph("<b>문제에서 찾는 말</b>", S(fontSize=9, leading=12, textColor=colors.white)),
             Paragraph("<b>세우는 식</b>", S(fontSize=9, leading=12, textColor=colors.white))]]
    kinds = [
        ("① 모두 몇 개", "모두, 합하면, 다 하면, 전부", "더하기  +"),
        ("② 남은 것", "남으면, 가져가면, 먹으면, 주면", "빼기  -"),
        ("③ 몇 개 더", "더 많다, 더 적다, 몇 개 더, 차", "큰 수 - 작은 수"),
        ("④ 모르는 수", "어떤 수, □, 모르는 수", "□를 가운데 두고 식 세우기"),
        ("⑤ 두 가지 읽기", "다른 말로, 고유어로, 한자어로", "이십삼 ↔ 스물셋"),
    ]
    for a, b, c in kinds:
        rows.append([Paragraph(a, S(fontSize=9, leading=13, textColor=NAVY)),
                     Paragraph(b, S(fontSize=9, leading=13)),
                     Paragraph(c, S(fontSize=9, leading=13, textColor=CORAL))])
    t = K.table(rows, [CW * 0.22, CW * 0.47, CW * 0.31], header=True, header_bg=NAVY,
                body_style=[("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")],
                row_h=22)
    st.append(t)
    st.append(gap(8))
    st.append(tip("문제를 읽을 때 <b>밑줄</b>을 그어 보세요. 무엇을 구하는지, 이미 알고 있는 수가 무엇인지 "
                  "표시해 두면 식이 저절로 보입니다."))
    st.append(gap(11))

    st.append(K.problem("15", "유형을 알아보고 식을 세워 풀어 보세요."))
    qs = [
        "① 지우는 사탕을 8개 가지고 있습니다. 엄마가 7개를 더 주었습니다. 지우가 가진 사탕은 모두 몇 개일까요?",
        "② 주머니에 구슬이 16개 있었습니다. 그중 9개를 동생에게 주었습니다. 남은 구슬은 몇 개일까요?",
        "③ 민서는 종이를 24장, 하늘이는 17장 가지고 있습니다. 누가 몇 장 더 많을까요?",
        "④ 어떤 수에 6을 더했더니 15가 되었습니다. 어떤 수는 얼마일까요?",
        "⑤ 지수는 13살, 동생은 7살입니다. 지수는 동생보다 몇 살 더 많을까요?",
        "⑥ 어항에 물고기가 45마리 있었습니다. 그중 18마리를 다른 어항으로 옮겼습니다. 남은 물고기는 몇 마리일까요?",
    ]
    for q in qs:
        st.append(KeepTogether([
            Paragraph(q, S(fontSize=9.6, leading=16)),
            gap(1),
            expr_line(),
        ]))
        st.append(gap(6))

    st.append(gap(4))
    st.append(K.problem("16", "다음 문제가 어느 유형인지 ①~④에서 골라 써 보세요."))
    for line in ["· 책이 14권, 공책이 9권 있습니다. 책이 공책보다 몇 권 더 많을까요?  (     )",
                 "· 친구에게 5개를 받았더니 12개가 되었습니다. 처음에 몇 개였을까요?  (     )"]:
        st.append(Paragraph(line, S(fontSize=9.4, leading=18)))
    st.append(Paragraph("① 모두 몇 개  ② 남은 것  ③ 몇 개 더  ④ 모르는 수",
                        S(fontSize=8.6, leading=14, textColor=GRAY)))
    st.append(gap(10))

    st.append(tip("여유가 있으면 오늘 배운 유형 중 하나를 골라 <b>내가 문제를 하나 만들어</b> 보세요. "
                  "만들고 나서 직접 풀어 보면 유형이 더 또렷해집니다."))

    st.append(PageBreak())

    # ---------------- answer key ----------------
    st += answer_block([
        ("1. 11~20 두 가지 읽기",
         "11 십일 / 열하나 · 12 십이 / 열둘 · 13 십삼 / 열셋 · 14 십사 / 열넷 · 15 십오 / 열다섯<br/>"
         "16 십육 / 열여섯 · 17 십칠 / 열일곱 · 18 십팔 / 열여덟 · 19 십구 / 열아홉 · 20 이십 / 스물"),
        ("2. 두 가지로 쓰기",
         "23 이십삼 / 스물셋 · 35 삼십오 / 서른다섯 · 42 사십이 / 마흔둘 · 27 이십칠 / 스물일곱 · 50 오십 / 쉰"),
        ("3. 연결하기", "스물하나-21 · 서른여덟-38 · 마흔둘-42 · 쉰-50 · 열다섯-15 · 이십구-29"),
        ("4. 수수께끼", "23(스물셋) · 25(스물다섯) · 42(마흔둘)"),
        ("5. 10이 되는 수", "7+3 · 6+4 · 9+1 · 6+4 · 8+2 · 3+7  (앞이 □인 문제: 6 · 4 · 7)"),
        ("6. □ 안의 수",
         "3 · 8 · 15 · 10 / 10 · 20 · 19 · 10 / 25 · 12 · 3 · 31<br/>"
         "25+25=50 · 38+12=50 · 47+3=50 · 19+31=50"),
        ("7. 크기 비교", "34<43 · 27=27 · 19<21 · 40>39 · 50>45 · 12<21"),
        ("8. 차례대로 쓰기", "25 26 27 28 29 30 31 32"),
        ("9. 생활 속 읽기", "삼 층(한자어) · 다섯 개(고유어) · 날짜는 한자어 (예: 11월 16일 → 십일월 십육일)"),
        ("10. 받아올림 없는 덧셈", "18 · 28 · 37 · 49 · 24 · 33"),
        ("11. 받아내림이 있는 뺄셈", "8 · 14 · 25 · 34 · 26 · 9"),
        ("12. 세로셈", "27+15=42 · 43-18=25 · 36+9=45"),
        ("13. 세 수의 계산", "6+7-4=9 · 15-8+3=10 · 9+8-10=7 · 20-6+5=19"),
        ("14. □ 안의 수", "8 · 8 · 17 · 9 · 9 · 8"),
        ("15. 유형별 문장제",
         "① 8+7=15(개) ② 16-9=7(개) ③ 24-17=7 → 민서가 7장 더 많습니다.<br/>"
         "④ □+6=15 → □=9 ⑤ 13-7=6(살) ⑥ 45-18=27(마리)"),
        ("16. 유형 찾기", "첫째 ③(몇 개 더) · 둘째 ④(모르는 수)"),
    ])
    return K.build_with_cover(os.path.join(OUT, "01_초1_덧뺄셈_50이하_두가지읽기.pdf"), meta, st)


# ============================================================== 학습지 02 ====
def pdf_02():
    meta = dict(
        title="교과서 어휘를 잡으면<br/>문장제가 보입니다",
        title_plain="02 교과서 어휘·문장제 핵심 찾기",
        short_title="02 교과서 어휘와 문장제",
        tag="12월 겨울방학 특강 · 유치부 · 초등 저학년",
        sub="평평한·굴곡진·굽은 선·곧은 선 + 문장제에서 버릴 것 버리는 연습",
        intro="수학 문제를 틀리는 까닭은 계산이 아니라 낱말일 때가 많습니다. "
              "'굽은 선'과 '곧은 선'을 구별하지 못하면 도형 문제를 읽을 수 없고, "
              "'평평한'과 '울퉁불퉁한'을 모르면 그림을 잘못 봅니다. "
              "이 학습지는 교과서에 자주 나오는 어휘를 그림과 함께 익히고, 문장제에서 필요 없는 정보를 지워 내는 연습을 담았습니다.",
        goals=[
            "선과 모양을 나타내는 교과서 어휘를 그림과 연결해 익혀요.",
            "낱말의 뜻을 알고 문장 속에서 바르게 써요.",
            "문장제에서 버릴 정보와 남길 조건을 구별해요.",
            "남긴 조건으로 식을 세우고 답을 써요.",
        ],
        steps=["선과 모양을 나타내는 어휘", "뜻을 헷갈리기 쉬운 교과서 어휘",
               "문장제에서 버릴 것 버리기", "유형별 문장제 연습", "정답과 풀이"],
    )

    st = []

    # ---------------- page: 01 선과 모양 어휘 ----------------
    st += K.section("01", "선과 모양을 나타내는 말", "그림을 보고 낱말의 뜻을 확인합니다.")
    st.append(P("교과서에는 모양을 설명하는 낱말이 자주 나옵니다. 낱말의 뜻을 정확히 알면 그림을 보고 "
                "바르게 고를 수 있습니다.", "body_j"))
    st.append(gap(8))
    st.append(K.PictoRow([
        dict(picto="straight", name="곧은 선"),
        dict(picto="curved", name="굽은 선"),
        dict(picto="flat", name="평평한"),
        dict(picto="hills", name="굴곡진"),
    ], card_h=72))
    st.append(gap(6))
    st.append(K.PictoRow([
        dict(picto="pointy", name="뾰족한"),
        dict(picto="round", name="둥근"),
        dict(picto="bumpy", name="울퉁불퉁한"),
        dict(picto="bend", name="꺾인 선"),
    ], card_h=72))
    st.append(gap(7))
    st.append(tip("'곧은 선'은 한 방향으로 뻗은 선, '평평한'은 높낮이가 같은 모양입니다."))
    st.append(gap(8))

    st.append(K.problem("1", "그림과 낱말을 알맞게 이어 보세요."))
    st.append(K.ConnectCols(
        ["곧은 선", "굽은 선", "평평한", "굴곡진", "뾰족한"],
        ["오르내림이 있는 산 모양", "한 방향으로 쭉 뻗은 선", "끝이 뾰죽한 모양",
         "밋밋하게 높낮이가 같은 모양", "부드럽게 휘어 있는 선"], row_h=23))
    st.append(gap(8))

    st.append(K.problem("2", "설명을 읽고 알맞은 낱말을 골라 동그라미 해 보세요."))
    for txt in ["밋밋하고 높낮이가 같은 모양은 ( 평평한 / 굴곡진 ) 모양입니다.",
                "부드럽게 휘어 있는 선은 ( 곧은 선 / 굽은 선 )입니다.",
                "산처럼 오르내리는 모양은 ( 평평한 / 굴곡진 ) 모양입니다."]:
        st.append(Paragraph("· " + txt, S(fontSize=9.6, leading=18)))
    st.append(gap(7))

    st.append(K.problem("3", "말에 맞게 직접 그려 보세요."))
    draw_rows = [[Paragraph(t, S(fontSize=8.6, leading=12, textColor=GRAY)) for t in
                  ["곧은 선", "굽은 선", "굴곡진 선", "평평한 모양"]], ["", "", "", ""]]
    st.append(K.table(draw_rows, [CW / 4] * 4, header=False, row_h=[15, 62],
                      body_style=[("VALIGN", (0, 0), (-1, -1), "TOP"),
                                  ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    st.append(gap(8))

    st.append(K.problem("4", "모양을 설명한 말이 맞으면 O, 틀리면 X를 써 보세요."))
    for line in ["· 자로 반듯하게 그은 선은 굽은 선입니다.  (     )",
                 "· 산처럼 오르내리는 모양은 굴곡진 모양입니다.  (     )",
                 "· 운동장처럼 높낮이가 같은 땅은 평평한 땅입니다.  (     )"]:
        st.append(Paragraph(line, S(fontSize=9.6, leading=18)))
    st.append(PageBreak())

    # ---------------- page: 02 교과서 어휘 ----------------
    st += K.section("02", "뜻을 헷갈리기 쉬운 교과서 어휘", "문장 속에서 낱말의 쓰임을 확인합니다.")
    st.append(P("같은 낱말도 수학 시간에는 조금 더 정확한 뜻으로 쓰입니다. 아래 낱말은 1~2학년 교과서에 자주 나오는 말입니다.",
                "body_j"))
    st.append(gap(6))
    st.append(K.ConnectCols(
        ["평평한", "굴곡진", "곧은 선", "굽은 선", "반듯한", "뾰족한", "둥근", "울퉁불퉁한"],
        ["부드럽게 휘어 있는 선", "높낮이가 같아 밋밋한 모양", "동그랗게 생긴 모양",
         "한 점에서 뾰죽하게 모인 모양", "휘어 있지 않고 쭉 뻗은 선", "바르고 기울지 않은 모양",
         "오르내리며 굽이진 모양", "표면이 고르지 않고 들쭉날쭉한 모양"], row_h=21))
    st.append(gap(8))

    st.append(K.problem("5", "□ 안에 알맞은 낱말을 골라 써 보세요."))
    st.append(Paragraph("보기 : 평평한 · 굴곡진 · 곧은 선 · 굽은 선 · 반듯한",
                        S(fontSize=9.2, leading=15, textColor=CORAL)))
    st.append(gap(2))
    for txt in ["· 운동장은 넓고 (            ) 땅입니다.",
                "· 지도에서 강은 (            )으로 흐르며 구불구불합니다.",
                "· 자로 그은 선은 (            )입니다.",
                "· 지우개를 오래 쓰면 모서리가 (            )이 아닙니다."]:
        st.append(Paragraph("· " + txt, S(fontSize=9.8, leading=19)))
    st.append(gap(8))

    st.append(K.problem("6", "낱말의 뜻을 내 말로 한 줄씩 써 보세요."))
    st.append(cells([["평평한", ""], ["굴곡진", ""], ["울퉁불퉁한", ""]],
                    ncols=1, cell_h=32, label_w=26 * mm, head=False))
    st.append(gap(8))
    st.append(K.problem("7", "글을 읽고, 낱말이 무엇을 설명하는지 찾아 써 보세요."))
    st.append(gap(3))
    st.append(K.box([
        Paragraph("우리 동네에는 넓고 <b>평평한</b> 운동장이 있습니다. 운동장 뒤에는 <b>굴곡진</b> 산이 있고, "
                  "산 아래로는 <b>굽은</b> 길이 이어집니다. 길가에는 나무를 <b>반듯하게</b> 세운 울타리가 있고, "
                  "끝이 <b>뾰족한</b> 나무도 서 있습니다. 비가 온 뒤라 길이 조금 <b>울퉁불퉁</b>합니다.",
                  S(fontSize=9.6, leading=18)),
    ], bg=CREAM, border=CORAL_LINE, pad=10))
    st.append(gap(6))
    for line in ["· 평평한 → (            )이/가 평평합니다.",
                 "· 굴곡진 → (            )이/가 굴곡져 있습니다.",
                 "· 울퉁불퉁한 → (            )이/가 울퉁불퉁합니다."]:
        st.append(Paragraph(line, S(fontSize=9.6, leading=19)))
    st.append(gap(8))

    st.append(PageBreak())

    # ---------------- page: 03 문장제 버리기 ----------------
    st += K.section("03", "문장제에서 버릴 것 버리기", "필요 없는 정보에 X표를 치고 조건만 남깁니다.")
    st.append(P("문장제가 어려운 까닭은 계산이 아니라 <b>정보가 많기 때문</b>입니다. "
                "문제를 풀 때는 ① 무엇을 묻는지 찾고 ② 필요 없는 정보에 X표를 치고 ③ 남은 수로 식을 세웁니다.",
                "body_j"))
    st.append(gap(6))
    st.append(K.box([
        Paragraph("<b>3단계로 풀어 보세요</b>", S(fontSize=9.4, leading=14, textColor=CORAL)),
        gap(3),
        Paragraph("① 묻는 것에 밑줄 : 구하는 것이 무엇인지 찾기<br/>"
                  "② 필요 없는 정보에 X : 답을 구하는 데 쓰이지 않는 말 지우기<br/>"
                  "③ 남은 수로 식 세우기 : 식을 쓰고 답에 단위 붙이기",
                  S(fontSize=9.2, leading=16)),
    ], bg=CREAM, border=CORAL_LINE, pad=9))
    st.append(gap(9))

    st.append(K.problem("8", "글을 읽고 필요 없는 정보에 X표를 한 뒤, 식을 세워 답을 구하세요."))
    problems = [
        ("①", "민준이는 사과 12개와 귤 7개를 샀습니다. 그중 사과 3개를 먹었습니다. 남은 사과는 몇 개일까요?"),
        ("②", "교실에 책상이 18개 있습니다. 그중 5개는 1학년 교실로 옮겼습니다. 교실에 남은 책상은 몇 개일까요?"),
        ("③", "가게에 빵이 15개 있었습니다. 오전에 빵 6개를 팔고, 손님에게서 20,000원을 받았습니다. 남은 빵은 몇 개일까요?"),
        ("④", "수정이는 우유 3개를 마시고 주머니에 사탕 5개와 초콜릿 2개를 넣었습니다. 처음에 초콜릿이 6개 있었다면 남은 초콜릿은 몇 개일까요?"),
        ("⑤", "민지네 반 학생 21명이 운동장에 나왔습니다. 그중 8명은 줄넘기를 하고 6명은 공놀이를 합니다. 줄넘기와 공놀이를 하지 않는 학생은 몇 명일까요?"),
        ("⑥", "어머니가 사과 20개를 사 오셨습니다. 그중 9개를 이웃에게 드리고, 아버지가 4개를 더 사 오셨습니다. 남은 사과는 몇 개일까요?"),
    ]
    for mark, q in problems:
        st.append(KeepTogether([
            Paragraph("<font color='#DE5B3C'>%s</font> %s" % (mark, q), S(fontSize=9.5, leading=16)),
            gap(1),
            Paragraph("필요 없는 정보 : ___________________________", S(fontSize=9, leading=14, textColor=GRAY)),
            expr_line(height=22),
        ]))
        st.append(gap(6))

    st.append(gap(2))
    st.append(note("버릴 정보는 <b>답을 구하는 데 쓰이지 않는 말</b>입니다. 사람 이름·물건 이름·이미 지난 일은 "
                   "대부분 버려도 됩니다. 단, 조건을 바꾸는 말('그중', '더')은 꼭 남겨야 합니다."))
    st.append(PageBreak())

    # ---------------- page: 04 유형별 문장제 ----------------
    st += K.section("04", "유형별 문장제 연습", "같은 문장제를 유형별로 나누어 풉니다.")
    st.append(P("문장제는 크게 네 가지로 나뉩니다. 어떤 유형인지 먼저 알아차리면 식을 세우는 시간이 짧아집니다.",
                "body_j"))
    st.append(gap(5))
    st.append(K.table([
        [Paragraph("<b>유형</b>", S(fontSize=9, leading=13, textColor=colors.white)),
         Paragraph("<b>찾는 말</b>", S(fontSize=9, leading=13, textColor=colors.white)),
         Paragraph("<b>식</b>", S(fontSize=9, leading=13, textColor=colors.white))],
        [Paragraph("합", S(fontSize=9, leading=13)), Paragraph("모두, 합하면", S(fontSize=9, leading=13)),
         Paragraph("더하기", S(fontSize=9, leading=13, textColor=CORAL))],
        [Paragraph("차", S(fontSize=9, leading=13)), Paragraph("남으면, 주면", S(fontSize=9, leading=13)),
         Paragraph("빼기", S(fontSize=9, leading=13, textColor=CORAL))],
        [Paragraph("비교", S(fontSize=9, leading=13)), Paragraph("더 많다, 몇 개 더", S(fontSize=9, leading=13)),
         Paragraph("큰 수 - 작은 수", S(fontSize=9, leading=13, textColor=CORAL))],
    ], [CW * 0.16, CW * 0.34, CW * 0.50], header=True, header_bg=NAVY,
        body_style=[("ALIGN", (0, 0), (-1, -1), "LEFT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")],
        row_h=22))
    st.append(gap(9))

    st.append(K.problem("9", "식을 세우고 답을 구하세요. 답에는 단위를 꼭 써 보세요."))
    qs = [
        ("①", "가게에 연필이 24자루 있었습니다. 오전에 9자루를 팔고 오후에 6자루를 더 팔았습니다. 남은 연필은 몇 자루일까요?"),
        ("②", "지민이는 색종이를 15장, 수아는 22장 가지고 있습니다. 색종이는 누가 몇 장 더 많을까요?"),
        ("③", "한 상자에 공이 10개씩 들어 있습니다. 상자 3개에 든 공은 모두 몇 개일까요?"),
        ("④", "버스에 18명이 타고 있었습니다. 정류장에서 6명이 내리고 4명이 탔습니다. 지금 버스에 타고 있는 사람은 몇 명일까요?"),
        ("⑤", "한 봉지에 구슬이 7개씩 들어 있습니다. 봉지 5개에 든 구슬은 모두 몇 개일까요?"),
        ("⑥", "물병에 물이 900mL 있었습니다. 그중 350mL를 마셨습니다. 남은 물은 몇 mL일까요?"),
    ]
    for mark, q in qs:
        st.append(KeepTogether([
            Paragraph("<font color='#DE5B3C'>%s</font> %s" % (mark, q), S(fontSize=9.5, leading=16)),
            gap(1),
            expr_line(height=22),
        ]))
        st.append(gap(7))

    st.append(gap(2))
    st.append(K.problem("10", "②번 문제에서 왜 빼기를 했는지, 내 생각을 한 줄로 써 보세요."))
    st.append(K.DottedLines(2, gap=21))
    st.append(gap(6))
    st.append(gap(4))
    st.append(K.problem("11", "배운 낱말 3개를 넣어 짧은 글을 지어 보세요."))
    st.append(K.DottedLines(3, gap=20))
    st.append(gap(4))
    st.append(tip("답을 쓸 때 <b>단위</b>(개, 자루, 장, 명)를 빠뜨리면 뜻이 달라집니다. 문제에 나온 단위를 그대로 가져다 쓰세요."))
    st.append(PageBreak())

    st += answer_block([
        ("1. 그림과 낱말 연결",
         "곧은 선-한 방향으로 쭉 뻗은 선 · 굽은 선-부드럽게 휘어 있는 선 · 평평한-밋밋하게 높낮이가 같은 모양 · "
         "굴곡진-오르내림이 있는 산 모양 · 뾰족한-끝이 뾰죽한 모양"),
        ("2. 낱말 고르기", "평평한 · 굽은 선 · 굴곡진"),
        ("3. 그려 보기", "선의 곧음/휘어짐, 면의 높낮이가 그림에 드러나면 정답입니다."),
        ("4. O·X", "① X ② O ③ O"),
        ("5. □ 안의 낱말", "평평한 · 굴곡진 · 곧은 선 · 반듯한"),
        ("6. 내 말로 뜻 쓰기",
         "평평한: 높낮이가 같아 밋밋한 모양 · 굴곡진: 오르내리며 굽이진 모양 · "
         "울퉁불퉁한: 표면이 고르지 않고 들쭉날쭉한 모양"),
        ("7. 글에서 찾기", "평평한-운동장 · 굴곡진-산 · 울퉁불퉁한-길"),
        ("8. 버릴 것 버리기",
         "① 버릴 것: 귤 7개 → 12-3=9(개)<br/>"
         "② 버릴 것: 없음 → 18-5=13(개)<br/>"
         "③ 버릴 것: 20,000원 → 15-6=9(개)<br/>"
         "④ 버릴 것: 우유 3개, 사탕 5개 → 6-2=4(개)<br/>"
         "⑤ 버릴 것: 없음 → 21-8-6=7(명)<br/>"
         "⑥ 버릴 것: 이웃·아버지(사람) → 20-9+4=15(개)"),
        ("9. 유형별 문장제",
         "① 24-9-6=9(자루) ② 22-15=7 → 수아가 7장 더 많습니다.<br/>"
         "③ 10+10+10=30(개) 또는 10×3=30(개) ④ 18-6+4=16(명)<br/>"
         "⑤ 7+7+7+7+7=35(개) 또는 7×5=35(개) ⑥ 900-350=550(mL)"),
        ("10. 왜 빼기를 했는지", "수아의 색종이에서 지민이의 색종이만큼 빼야 '몇 장 더 많은지'를 알 수 있기 때문입니다."),
        ("11. 짧은 글 짓기", "배운 낱말 3개 이상이 바른 뜻으로 들어 있으면 좋습니다. "
                        "(예: 운동장은 평평하고, 뒤에는 굴곡진 산이 있습니다.)"),
    ])
    return K.build_with_cover(os.path.join(OUT, "02_초등_교과서어휘_문장제핵심찾기.pdf"), meta, st)


# ============================================================== 학습지 03 ====
def pdf_03():
    meta = dict(
        title="그림에서 글자로,<br/>상형문자 이야기 한자",
        title_plain="03 상형문자 스토리 배경지식 한자",
        short_title="03 상형문자 이야기 한자",
        tag="12월 겨울방학 특강 · 유치부 · 초등 저학년",
        sub="日·月·山·川·木·火·水·人 — 초등 저학년이 꼭 알아 두면 좋은 한자",
        intro="한자는 처음부터 외우는 글자가 아닙니다. 사물의 모양을 그린 그림이 오늘날의 글자가 되었기 때문입니다. "
              "그림과 이야기를 함께 보면 글자의 생김새가 저절로 기억에 남고, 낱말의 뜻을 짐작하는 힘(배경지식)이 자랍니다. "
              "국어사전을 찾지 않아도 '산수', '일기', '화력' 같은 말의 뜻을 풀어 낼 수 있게 됩니다.",
        goals=[
            "여덟 글자의 상형문자가 어떤 그림에서 왔는지 이야기로 익혀요.",
            "글자의 뜻을 알고, 그 글자가 들어간 낱말을 풀어 봐요.",
            "한자 어휘를 통해 문장의 뜻을 짐작하는 힘을 길러요.",
        ],
        steps=["그림에서 글자로 : 日·月·山·川", "그림에서 글자로 : 木·火·水·人",
               "그림과 글자 연결하기", "한자로 만든 낱말 익히기", "정답과 풀이"],
    )

    st = []
    cards = [
        ("日", "sun", "해 일", "해의 둥근 모양을 그리고 가운데 점을 찍었습니다. "
                          "오늘날에는 네모 안에 줄을 그은 모양이 되었습니다.",
         "날마다 → 매일(每日) · 하루를 적은 글 → 일기(日記)"),
        ("月", "moon", "달 월", "가느다란 초승달 모양을 그대로 옮겼습니다. "
                            "달은 밤을 밝히는 것이라 '달 월'이 되었습니다.",
         "한 달 → 월(月) · 달력 → 월력(月曆)"),
        ("山", "mountain", "뫼 산", "산봉우리 세 개가 솟은 모양입니다. "
                                "가운데 봉우리가 가장 높습니다.",
         "산과 물 → 산수(山水) · 등산(登山)"),
        ("川", "river", "내 천", "물이 세 갈래로 흐르는 모양을 그렸습니다. "
                              "흐르는 물길을 뜻합니다.",
         "개천 → 천(川) · 하천(河川)"),
    ]

    st += K.section("01", "그림에서 글자로 ①", "해·달·산·내, 네 글자의 이야기입니다.")
    for char_, picto, name, story, words in cards:
        st.append(K.box([
            two_col([
                K.PictoRow([dict(picto=picto)], card_h=64, card_w=64, show_char=False),
                gap(4),
                Paragraph("그림", S(fontSize=8, leading=11, textColor=GRAY, alignment=1)),
            ], [
                Paragraph("<font name='KRS' size='30'>%s</font>&nbsp;&nbsp;"
                          "<font color='#DE5B3C'><b>%s</b></font>" % (char_, name),
                          S(fontSize=13, leading=34)),
                gap(2),
                Paragraph(story, S(fontSize=9.2, leading=16)),
                gap(2),
                Paragraph("<font color='#3F7D6B'>%s</font>" % words,
                          S(fontSize=8.8, leading=13.5)),
            ], ratio=0.21, pad=14),
        ], bg=CREAM, border=CORAL_LINE, pad=10))
        st.append(gap(8))

    st.append(Paragraph("따라 쓰기 — 글자의 모양을 보고 네 번씩 써 보세요.", S(fontName="KRB", fontSize=10.5, leading=16, textColor=CORAL)))
    st.append(gap(4))
    st.append(trace_grid([("日", "해 일"), ("月", "달 월"), ("山", "뫼 산"), ("川", "내 천")], cells=4))
    st.append(PageBreak())

    st += K.section("02", "그림에서 글자로 ②", "나무·불·물·사람, 네 글자의 이야기입니다.")
    cards2 = [
        ("木", "tree", "나무 목", "줄기와 가지, 뿌리를 그린 모양입니다. "
                                "가운데 세로줄이 줄기, 가로줄이 가지입니다.",
         "나무 → 목(木) · 목재(木材)"),
        ("火", "fire", "불 화", "타오르는 불꽃의 모양을 그렸습니다. "
                              "불꽃이 위로 솟는 모습이 남아 있습니다.",
         "불의 힘 → 화력(火力) · 화산(火山)"),
        ("水", "water", "물 수", "가운데로 흐르는 물줄기와 양옆의 물방울을 그렸습니다.",
         "물 → 수(水) · 홍수(洪水) · 수영(水泳)"),
        ("人", "person", "사람 인", "두 다리로 서 있는 사람의 옆모습을 그렸습니다.",
         "사람 수 → 인구(人口) · 인사(人事)"),
    ]
    for char_, picto, name, story, words in cards2:
        st.append(K.box([
            two_col([
                K.PictoRow([dict(picto=picto)], card_h=64, card_w=64, show_char=False),
                gap(4),
                Paragraph("그림", S(fontSize=8, leading=11, textColor=GRAY, alignment=1)),
            ], [
                Paragraph("<font name='KRS' size='30'>%s</font>&nbsp;&nbsp;"
                          "<font color='#DE5B3C'><b>%s</b></font>" % (char_, name),
                          S(fontSize=13, leading=34)),
                gap(2),
                Paragraph(story, S(fontSize=9.2, leading=16)),
                gap(2),
                Paragraph("<font color='#3F7D6B'>%s</font>" % words,
                          S(fontSize=8.8, leading=13.5)),
            ], ratio=0.24, pad=12),
        ], bg=CREAM, border=CORAL_LINE, pad=9))
        st.append(gap(7))

    st.append(Paragraph("따라 쓰기 — 글자의 모양을 보고 네 번씩 써 보세요.", S(fontName="KRB", fontSize=10.5, leading=16, textColor=CORAL)))
    st.append(gap(4))
    st.append(trace_grid([("木", "나무 목"), ("火", "불 화"), ("水", "물 수"), ("人", "사람 인")], cells=4))
    st.append(gap(8))
    st.append(tip("위·아래를 뜻하는 <font name='KRS'>上·下</font>도 그림에서 왔습니다. 기준선 위에 점을 찍으면 上(위 상), "
                  "아래에 점을 찍으면 下(아래 하)입니다."))
    st.append(PageBreak())

    # ---------------- page: 03 문제 ----------------
    st += K.section("03", "그림과 글자, 뜻을 이어 보기", "배운 글자를 스스로 확인합니다.")
    st.append(K.problem("1", "그림을 보고 알맞은 한자를 골라 써 보세요."))
    st.append(K.PictoRow([
        dict(picto="sun", name="(      )"), dict(picto="moon", name="(      )"),
        dict(picto="tree", name="(      )"), dict(picto="person", name="(      )"),
    ], card_h=70, show_char=False))
    st.append(gap(4))
    st.append(Paragraph("보기 : 日 · 月 · 山 · 川 · 木 · 火 · 水 · 人",
                        S(fontSize=10, leading=15, textColor=CORAL, alignment=1)))
    st.append(gap(11))

    st.append(K.problem("2", "글자와 뜻을 이어 보세요."))
    st.append(K.ConnectCols(["日", "月", "山", "川", "火", "人"],
                            ["사람", "불", "해", "내(물길)", "달", "산"]))
    st.append(gap(10))

    st.append(K.problem("3", "글자의 뜻을 우리말로 써 보세요."))
    st.append(cells([["水", "木", "山", "月"], ["", "", "", ""]], ncols=4, cell_h=30, label_w=0, head=False))
    st.append(gap(11))

    st.append(K.problem("4", "한자로 된 낱말의 뜻을 골라 ○표 해 보세요."))
    for w, opts in [("日記", "① 날마다 쓰는 책  ② 하루 동안의 기록"),
                    ("山水", "① 산과 물  ② 물에 사는 동물"),
                    ("火力", "① 불의 힘  ② 불을 끄는 일")]:
        st.append(Paragraph("<b>%s</b>&nbsp;&nbsp;%s" % (w, opts), S(fontSize=10, leading=18)))
        st.append(gap(2))
    st.append(gap(10))

    st.append(K.problem("5", "받아쓰기 — 뜻을 읽고 알맞은 한자를 써 보세요."))
    rows = [[Paragraph("<b>해</b>", S(fontSize=9.2, leading=13)), "",
             Paragraph("<b>달</b>", S(fontSize=9.2, leading=13)), "",],
            [Paragraph("<b>산</b>", S(fontSize=9.2, leading=13)), "",
             Paragraph("<b>내</b>", S(fontSize=9.2, leading=13)), ""],
            [Paragraph("<b>나무</b>", S(fontSize=9.2, leading=13)), "",
             Paragraph("<b>불</b>", S(fontSize=9.2, leading=13)), ""],
            [Paragraph("<b>물</b>", S(fontSize=9.2, leading=13)), "",
             Paragraph("<b>사람</b>", S(fontSize=9.2, leading=13)), ""]]
    st.append(K.table(rows, [22 * mm, (CW - 44 * mm) / 2, 22 * mm, (CW - 44 * mm) / 2],
                      header=False, row_h=34,
                      body_style=[("BACKGROUND", (0, 0), (0, -1), CREAM_DEEP),
                                  ("BACKGROUND", (2, 0), (2, -1), CREAM_DEEP)]))
    st.append(gap(10))

    st.append(PageBreak())

    # ---------------- page: 04 어휘 ----------------
    st += K.section("04", "한자로 만든 낱말 익히기", "두 글자가 만나 새로운 뜻이 됩니다.")
    st.append(P("한자는 두 글자가 만나 새로운 낱말을 만듭니다. 아래 낱말을 소리 내어 읽고 뜻을 확인해 보세요.",
                "body_j"))
    st.append(gap(6))
    st.append(K.problem("6", "한자로 된 낱말을 바르게 읽은 것을 골라 ○표 해 보세요."))
    for w, opts in [("日記", "① 일기    ② 일상"), ("人口", "① 인사    ② 인구"),
                    ("山水", "① 산수    ② 수산")]:
        st.append(Paragraph("<font name='KRS'>%s</font>&nbsp;&nbsp;%s" % (w, opts),
                            S(fontSize=9.8, leading=19)))
    st.append(gap(8))
    st.append(note("한자를 알면 처음 보는 낱말도 뜻을 짐작할 수 있습니다. "
                   "예) 山(산) + 水(물) = 山水(산수, 산과 물)"))
    st.append(gap(10))
    rows = [[Paragraph("<b>낱말</b>", S(fontSize=9.2, leading=13, textColor=colors.white)),
             Paragraph("<b>읽기</b>", S(fontSize=9.2, leading=13, textColor=colors.white)),
             Paragraph("<b>뜻</b>", S(fontSize=9.2, leading=13, textColor=colors.white))]]
    for w, r, m in [("日記", "일기", "하루 동안 있었던 일을 적은 기록"),
                    ("山水", "산수", "산과 물, 또는 산과 물의 경치"),
                    ("火力", "화력", "불이 내는 힘"),
                    ("人口", "인구", "한 지역에 사는 사람의 수"),
                    ("出入", "출입", "나가고 들어옴"),
                    ("上下", "상하", "위와 아래")]:
        rows.append([Paragraph("<font name='KRS' size='11'>%s</font>" % w, S(fontSize=10, leading=14)),
                     Paragraph(r, S(fontSize=9.4, leading=14, textColor=CORAL)),
                     Paragraph(m, S(fontSize=9.2, leading=14))])
    st.append(K.table(rows, [CW * 0.18, CW * 0.16, CW * 0.66], header=True, header_bg=NAVY,
                      body_style=[("ALIGN", (0, 0), (-1, -1), "LEFT"),
                                  ("VALIGN", (0, 0), (-1, -1), "MIDDLE")], row_h=23))
    st.append(gap(10))

    st.append(K.problem("7", "낱말의 뜻을 골라 이어 보세요."))
    st.append(K.ConnectCols(["日記", "人口", "出入", "山水"],
                            ["나가고 들어옴", "하루의 기록", "산과 물의 경치", "사는 사람의 수"]))
    st.append(gap(10))

    st.append(K.problem("8", "두 글자가 만나 새 낱말이 됩니다. □ 안에 알맞은 낱말을 써 보세요."))
    for exp in ["日(해) + 記(기록할) = □", "山(산) + 水(물) = □",
                "火(불) + 力(힘) = □", "人(사람) + 口(입) = □"]:
        st.append(Paragraph("· " + exp, S(fontSize=9.8, leading=19)))
    st.append(gap(10))

    st.append(PageBreak())

    st += K.section("05", "오늘 배운 글자 정리", "표를 채우며 스스로 확인합니다.")
    rows = [[Paragraph("<b>글자</b>", S(fontSize=9.2, leading=13, textColor=colors.white)),
             Paragraph("<b>뜻</b>", S(fontSize=9.2, leading=13, textColor=colors.white)),
             Paragraph("<b>이 글자가 들어간 낱말</b>", S(fontSize=9.2, leading=13, textColor=colors.white))]]
    for ch in ["日", "月", "山", "川", "木", "火", "水", "人"]:
        rows.append([Paragraph("<font name='KRS' size='14'>%s</font>" % ch, S(fontSize=11, leading=16)),
                     "", ""])
    st.append(K.table(rows, [20 * mm, 30 * mm, CW - 50 * mm], header=True, header_bg=NAVY,
                      row_h=30, body_style=[("ALIGN", (0, 0), (0, -1), "CENTER")]))
    st.append(gap(12))

    st.append(K.problem("9", "배운 한자로 짧은 글을 지어 보세요. (두 문장 이상)"))
    st.append(Paragraph("보기 : 아침에 일기를 썼습니다. 오늘은 가족과 산에 갔습니다.",
                        S(fontSize=9, leading=14, textColor=GRAY)))
    st.append(gap(3))
    st.append(K.DottedLines(4, gap=22))
    st.append(gap(10))
    st.append(tip("한자를 쓸 때는 <b>획순</b>을 지켜 천천히 써 보세요. 획순을 지키면 글자가 반듯해지고 기억에도 오래 남습니다."))
    st.append(PageBreak())

    st += answer_block([
        ("1. 그림 보고 한자 쓰기", "日(해) · 月(달) · 木(나무) · 人(사람)"),
        ("2. 글자와 뜻 연결", "日-해 · 月-달 · 山-산 · 川-내(물길) · 火-불 · 人-사람"),
        ("3. 뜻 쓰기", "水 물 · 木 나무 · 山 산 · 月 달"),
        ("4. 낱말의 뜻", "日記 ② · 山水 ① · 火力 ①"),
        ("5. 받아쓰기", "해 日 · 달 月 · 산 山 · 내 川 · 나무 木 · 불 火 · 물 水 · 사람 人"),
        ("6. 바르게 읽기", "日記 ① · 人口 ② · 山水 ①"),
        ("7. 낱말과 뜻 연결", "日記-하루의 기록 · 人口-사는 사람의 수 · 出入-나가고 들어옴 · 山水-산과 물의 경치"),
        ("8. 새 낱말 만들기", "日記(일기) · 山水(산수) · 火力(화력) · 人口(인구)"),
        ("9. 짧은 글", "배운 한자가 들어간 낱말(일기·산수·화력·인구 등)을 한 개 이상 사용해 두 문장 이상 쓰면 정답입니다."),
    ])
    return K.build_with_cover(os.path.join(OUT, "03_상형문자_스토리_배경지식_한자.pdf"), meta, st)


# ============================================================== 학습지 04 ====
def pdf_04():
    meta = dict(
        title="왜 그렇게 생각했는지<br/>문장으로 쓰는 연습",
        title_plain="04 서술형 표현 공부 워크시트",
        short_title="04 서술형·표현 공부",
        tag="12월 겨울방학 특강 · 초등 1~3학년",
        sub="식과 문장을 함께 쓰는 서술형·표현 공부 4단계",
        intro="서술형 문제가 어려운 까닭은 '무엇부터 써야 할지'를 몰라서입니다. "
              "이 학습지는 ① 묻는 것 찾기 ② 주어진 것 정리하기 ③ 식 쓰기 ④ 까닭 쓰기, 네 칸으로 나누어 "
              "생각을 차례대로 적도록 만들었습니다. 네 칸을 채우다 보면 자연스럽게 완성된 서술형 답이 됩니다.",
        goals=[
            "문제에서 묻는 것과 주어진 것을 구별해 표시해요.",
            "식과 문장을 함께 써서 풀이 과정을 남겨요.",
            "왜 그렇게 생각했는지 내 말로 설명해요.",
            "문장을 늘리고 잇는 표현 연습을 해요.",
        ],
        steps=["서술형 4단계 익히기", "4단계로 풀어 보기 ①·②", "4단계로 풀어 보기 ③·④",
               "표현을 늘리는 연습", "정답과 예시"],
    )

    st = []
    st += K.section("01", "서술형 4단계", "답을 쓰기 전에 생각을 정리합니다.")
    st.append(P("서술형 답안은 한 번에 쓰지 않습니다. 아래 네 칸을 차례로 채우면 답안이 완성됩니다.",
                "body_j"))
    st.append(gap(8))
    steps = [("①", "묻는 것 찾기", "구하는 것이 무엇인지, 무엇을 말해야 하는지 표시합니다."),
             ("②", "주어진 것 정리", "알고 있는 수와 조건을 골라 씁니다. 필요 없는 정보는 버립니다."),
             ("③", "식 쓰기", "어떤 계산을 했는지 식으로 남깁니다."),
             ("④", "까닭 쓰기", "왜 그런 식을 세웠는지, 왜 그렇게 생각했는지 문장으로 씁니다.")]
    rows = [[Paragraph("<font color='#FFFFFF'><b>%s</b></font>" % a, S(fontSize=11, leading=16)),
             Paragraph("<b>%s</b>" % b, S(fontSize=9.6, leading=16, textColor=NAVY)),
             Paragraph(c, S(fontSize=9.2, leading=15))] for a, b, c in steps]
    st.append(K.table(rows, [12 * mm, 34 * mm, CW - 46 * mm], header=False, row_h=34,
                      body_style=[("BACKGROUND", (0, 0), (0, -1), CORAL),
                                  ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                  ("ALIGN", (0, 0), (0, -1), "CENTER")]))
    st.append(gap(10))

    st.append(Paragraph("함께 풀어 보기", S(fontName="KRB", fontSize=11, leading=16, textColor=CORAL)))
    st.append(gap(3))
    st.append(K.box([
        Paragraph("지호는 구슬을 14개 가지고 있었습니다. 친구에게 6개를 주었더니 할머니가 5개를 더 주셨습니다. "
                  "지호가 가진 구슬은 몇 개일까요? 왜 그렇게 생각했는지 쓰세요.", S(fontSize=9.6, leading=16)),
        gap(6),
        Paragraph("<font color='#DE5B3C'><b>①</b></font> 묻는 것 : 지호가 가진 구슬의 수", S(fontSize=9.2, leading=15)),
        Paragraph("<font color='#DE5B3C'><b>②</b></font> 주어진 것 : 처음 14개, 준 6개, 받은 5개", S(fontSize=9.2, leading=15)),
        Paragraph("<font color='#DE5B3C'><b>③</b></font> 식 : 14 - 6 + 5 = 13", S(fontSize=9.2, leading=15)),
        Paragraph("<font color='#DE5B3C'><b>④</b></font> 까닭 : 14개에서 6개를 주었으므로 빼고, 다시 5개를 받았으므로 더했습니다. "
                  "그래서 13개입니다.", S(fontSize=9.2, leading=15)),
    ], bg=CREAM, border=CORAL_LINE, pad=9))
    st.append(gap(12))

    st.append(Paragraph("까닭을 나타내는 말", S(fontName="KRB", fontSize=11, leading=16, textColor=CORAL)))
    st.append(gap(3))
    st.append(K.box([
        Paragraph("왜냐하면 · ~해서 · ~이므로 · ~때문에 · ~니까 · ~기 때문입니다", S(fontSize=9.6, leading=16)),
        gap(4),
        Paragraph("예) 14개에서 6개를 주었으므로 빼고, 5개를 받았기 때문에 더했습니다. "
                  "그래서 13개입니다.", S(fontSize=9.2, leading=15, textColor=GRAY)),
    ], bg=MINT_SOFT, border=colors.HexColor("#BFD9CE"), pad=9))
    st.append(gap(8))
    st.append(K.problem("1", "까닭을 나타내는 말을 넣어 문장을 완성해 보세요."))
    for t_ in ["· 비가 왔습니다. (            ) 우산을 챙겼습니다.",
               "· 열심히 연습했습니다. (            ) 시합에서 이겼습니다."]:
        st.append(Paragraph(t_, S(fontSize=9.6, leading=20)))
    st.append(gap(10))
    st.append(K.box([
        Paragraph("<b>말로 먼저 연습해 보세요</b>", S(fontSize=9.4, leading=14, textColor=CORAL)),
        gap(3),
        Paragraph("아래 네 가지를 선생님·부모님께 소리 내어 말해 보세요. 다 말했으면 네모에 표시합니다.<br/>"
                  "① 무엇을 묻는지  ② 무엇을 알고 있는지  ③ 어떤 식을 세웠는지  ④ 왜 그렇게 했는지",
                  S(fontSize=9.2, leading=16)),
        gap(3),
        Paragraph("□ □ □ □", S(fontSize=13, leading=18, textColor=GRAY)),
    ], bg=CREAM, border=CORAL_LINE, pad=9))
    st.append(PageBreak())

    # ---------------- page 02: 4단계 워크시트 ①② ----------------
    st += K.section("02", "4단계로 풀어 보기 ①·②", "칸을 하나씩 채워 봅니다.")

    def four_step(no, q):
        block = [K.problem(no, q), gap(2)]
        labels = ["① 묻는 것", "② 주어진 것", "③ 식", "④ 까닭"]
        rows = [[Paragraph(labels[0], S(fontSize=8.6, leading=12, textColor=CORAL)),
                 Paragraph(labels[1], S(fontSize=8.6, leading=12, textColor=CORAL))],
                ["", ""],
                [Paragraph(labels[2], S(fontSize=8.6, leading=12, textColor=CORAL)),
                 Paragraph(labels[3], S(fontSize=8.6, leading=12, textColor=CORAL))],
                ["", ""]]
        t = K.table(rows, [CW / 2, CW / 2], header=False, row_h=[16, 44, 16, 92],
                    body_style=[("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("BACKGROUND", (0, 0), (-1, 0), CREAM_DEEP),
                                ("BACKGROUND", (0, 2), (-1, 2), CREAM_DEEP)])
        block.append(t)
        return block

    st.extend(four_step("1", "수아네 반에는 학생이 24명 있습니다. 그중 9명이 축구를 좋아하고, 7명이 농구를 좋아합니다. "
                             "축구를 좋아하는 학생은 농구를 좋아하는 학생보다 몇 명 더 많을까요? 왜 그렇게 생각했는지 쓰세요."))
    st.append(gap(12))
    st.extend(four_step("2", "한 봉지에 사탕이 10개씩 들어 있습니다. 봉지 4개를 열었습니다. 그중 13개를 먹었다면 남은 사탕은 몇 개일까요? "
                             "어떤 순서로 계산했는지 쓰세요."))
    st.append(PageBreak())

    # ---------------- page 03: ③④ ----------------
    st += K.section("03", "4단계로 풀어 보기 ③·④", "조건이 두 개인 문제에 도전합니다.")
    st.extend(four_step("3", "문구점에서 공책 한 권에 5백 원짜리 3권과 1천 원짜리 1권을 샀습니다. "
                             "모두 얼마를 냈을까요? 왜 그렇게 계산했는지 쓰세요."))
    st.append(gap(12))
    st.extend(four_step("4", "어떤 수에 8을 더했더니 21이 되었습니다. 어떤 수는 얼마인지 풀이 과정과 함께 쓰세요."))
    st.append(gap(10))
    st.append(gap(10))

    st.append(Paragraph("좋은 답안과 아쉬운 답안", S(fontName="KRB", fontSize=11, leading=16, textColor=CORAL)))
    st.append(gap(4))
    cmp_rows = [
        [Paragraph("<b>아쉬운 답안</b>", S(fontSize=9.2, leading=14, textColor=GRAY)),
         Paragraph("<b>좋은 답안</b>", S(fontSize=9.2, leading=14, textColor=CORAL))],
        [Paragraph("13개입니다.", S(fontSize=9.4, leading=15)),
         Paragraph("구슬 14개에서 6개를 주었으므로 14-6=8이고, 할머니께 5개를 더 받았으므로 "
                   "8+5=13입니다. 그래서 13개입니다.", S(fontSize=9.4, leading=15))],
        [Paragraph("· 식이 없어 어떻게 풀었는지 알 수 없어요.<br/>· 까닭이 없어 생각이 드러나지 않아요.",
                   S(fontSize=8.6, leading=13, textColor=GRAY)),
         Paragraph("· 식이 있어 풀이 과정이 보여요.<br/>· 까닭을 나타내는 말로 생각이 드러나요.",
                   S(fontSize=8.6, leading=13, textColor=MINT))],
    ]
    st.append(K.table(cmp_rows, [CW / 2, CW / 2], header=False, row_h=[18, 62, 40],
                      body_style=[("VALIGN", (0, 0), (-1, -1), "TOP"),
                                  ("BACKGROUND", (1, 0), (1, 0), CREAM)]))
    st.append(tip("'왜'를 묻는 문제는 <b>까닭을 나타내는 말</b>(~해서, ~이므로, ~때문에)로 시작하면 문장이 자연스러워집니다."))
    st.append(PageBreak())

    # ---------------- page 04: 표현 ----------------
    st += K.section("04", "표현을 늘리는 연습", "짧은 문장을 풍부한 문장으로 만듭니다.")
    st.append(P("같은 내용도 낱말을 더하면 훨씬 자세해집니다. 누가·무엇을·어떻게·왜를 차례로 붙여 보세요.",
                "body_j"))
    st.append(gap(8))

    st.append(K.problem("5", "짧은 문장을 자세한 문장으로 늘려 써 보세요."))
    st.append(Paragraph("보기 : 새가 난다. → 작은 참새 한 마리가 나뭇가지에서 힘차게 난다.",
                        S(fontSize=9, leading=14, textColor=GRAY)))
    st.append(gap(4))
    st.append(K.table([
        [Paragraph("① 친구가 웃었다.", S(fontSize=9.6, leading=15)), ""],
        [Paragraph("② 비가 온다.", S(fontSize=9.6, leading=15)), ""],
        [Paragraph("③ 엄마가 밥을 하셨다.", S(fontSize=9.6, leading=15)), ""],
    ], [CW * 0.34, CW * 0.66], header=False, row_h=52,
        body_style=[("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    st.append(gap(10))

    st.append(K.problem("6", "두 문장을 이어 주는 말로 자연스럽게 이어 보세요. (그래서 / 그러나 / 왜냐하면)"))
    for t_ in ["비가 많이 왔다. (        ) 우산을 챙겼다.",
               "열심히 연습했다. (        ) 시합에서 졌다.",
               "일찍 잤다. (        ) 오늘 아침이 개운했다.",
               "책을 읽었다. (        ) 글쓰기를 잘하게 되었다."]:
        st.append(Paragraph("· " + t_, S(fontSize=9.8, leading=21)))
    st.append(gap(9))

    st.append(K.problem("7", "그림이나 생각을 자유롭게 표현해 보세요. (제목을 붙여도 좋습니다)"))
    st.append(Paragraph("제목 : ______________________________________________", S(fontSize=9.6, leading=18)))
    st.append(gap(2))
    st.append(K.DottedLines(7, gap=21))
    st.append(gap(10))

    st.append(K.problem("8", "어색한 문장을 바르게 고쳐 써 보세요."))
    for q, hint in [("① 나는 어제 학교에 갔다 왔다 갔다 했습니다.", "고친 문장 : "),
                    ("② 동생이 웃었다 너무 귀여웠다.", "고친 문장 : ")]:
        st.append(Paragraph(q, S(fontSize=9.6, leading=18)))
        st.append(Paragraph(hint + "____________________________", S(fontSize=9.4, leading=20, textColor=GRAY)))
        st.append(gap(4))
    st.append(PageBreak())

    st += answer_block([
        ("1. 수아네 반",
         "① 묻는 것: 축구를 좋아하는 학생이 농구를 좋아하는 학생보다 몇 명 더 많은지<br/>"
         "② 주어진 것: 전체 24명, 축구 9명, 농구 7명 (24명은 답을 구하는 데 쓰이지 않습니다)<br/>"
         "③ 식: 9 - 7 = 2  ④ 까닭: 축구를 좋아하는 학생 9명에서 농구를 좋아하는 학생 7명을 빼면 되기 때문입니다."),
        ("2. 사탕",
         "① 묻는 것: 남은 사탕의 수  ② 주어진 것: 한 봉지 10개, 4봉지, 먹은 13개<br/>"
         "③ 식: 10 × 4 = 40, 40 - 13 = 27  ④ 까닭: 먼저 전체 사탕 수를 구하고 먹은 만큼 빼야 하기 때문입니다."),
        ("3. 문구점",
         "① 묻는 것: 모두 낸 돈  ② 주어진 것: 5백 원짜리 3권, 1천 원짜리 1권<br/>"
         "③ 식: 500 × 3 = 1500, 1500 + 1000 = 2500  ④ 까닭: 공책 값을 각각 구해 더해야 하기 때문입니다."),
        ("4. 어떤 수",
         "① 묻는 것: 어떤 수  ② 주어진 것: 8을 더했더니 21<br/>"
         "③ 식: □ + 8 = 21 → 21 - 8 = 13  ④ 까닭: 더해서 21이 되었으므로 21에서 8을 빼면 처음 수가 됩니다."),
        ("5. 문장 늘리기 (예시)",
         "① 놀이터에서 친구가 환하게 웃었다. ② 아침부터 보슬보슬 비가 온다. ③ 엄마가 정성껏 맛있는 밥을 하셨다. "
         "(누가·언제·어디서·어떻게가 들어가면 좋습니다)"),
        ("6. 이어 주는 말", "① 그래서 ② 그러나 ③ 그래서 (왜냐하면을 쓰려면 뒤에 까닭이 이어져야 합니다)"),
        ("7. 자유 표현", "제목이 있고, 두 문장 이상으로 자신의 생각이 드러나면 좋습니다."),
    ])
    return K.build_with_cover(os.path.join(OUT, "04_서술형_표현공부_워크시트.pdf"), meta, st)


BUILDERS = {"1": pdf_01, "2": pdf_02, "3": pdf_03, "4": pdf_04}


def main(argv):
    which = argv[1:] or list(BUILDERS)
    made = []
    for key in which:
        path = BUILDERS[key]()
        made.append(path)
        print("wrote", path)
    return made


if __name__ == "__main__":
    main(sys.argv)
