#!/usr/bin/env python3
"""유치 6~7세 눈높이 놀이형 워크북 4종 생성기.

    python3 tools/build_pdfs_kids.py        # 4종 모두
    python3 tools/build_pdfs_kids.py 1      # 1번만
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, Spacer, Table, TableStyle

import pdfkit as K
import kidkit as D
from kidkit import (CORAL, CORAL_DEEP, CORAL_SOFT, CREAM, CREAM_2, CW, GRAY, INK,
                    LINE, MINT, MINT_SOFT, NAVY, NAVY_SOFT, PINK, PINK_SOFT,
                    PURPLE, PURPLE_SOFT, SKY, SKY_SOFT, YELLOW, YELLOW_SOFT)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "downloads")
os.makedirs(OUT, exist_ok=True)

S = D.st


def g(h=10):
    return Spacer(1, h)


def pic_row(items, height=110):
    """그림 카드 줄 — items: [(picto, caption, color)]"""
    return D.PictoBigRow(items, height=height)


class PictoBigRow(D.Flowable):
    def __init__(self, items, height=110, gap=10):
        super().__init__()
        self.items = items
        self.height = height
        self.gap = gap

    def wrap(self, aw, ah):
        n = len(self.items)
        self.cw = (aw - self.gap * (n - 1)) / n
        self.w = aw
        return self.w, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        for i, (picto, caption, colr) in enumerate(self.items):
            x = i * (self.cw + self.gap)
            c.setFillColor(colors.white)
            c.setStrokeColor(colr)
            c.setLineWidth(2.2)
            c.roundRect(x, 0, self.cw, self.height, 16, stroke=1, fill=1)
            D.K.draw_picto(c, picto, x + 8, self.height * 0.30, self.cw - 16, self.height * 0.52,
                           color=colr, lw=5)
            c.setFont("KRB", 15)
            c.setFillColor(NAVY)
            c.drawCentredString(x + self.cw / 2, 12, caption)
        c.restoreState()


D.PictoBigRow = PictoBigRow


def big_cards(items, cols=2, cell_h=120, gap=10):
    """큰 문제 카드 (식 + 답 칸)."""
    return D.ItemRow(items, cols=cols, cell_h=cell_h)


def answer_page(rows, color=CORAL_DEEP):
    page = list(D.mission_head("정답", "정답과 풀이", "먼저 스스로 풀어 본 뒤에 확인해 보세요."))
    body = []
    for head, body_text in rows:
        body.append(Paragraph(head, S("ah%d" % id(head), 15, 21, "KRB", color)))
        body.append(g(2))
        body.append(Paragraph(body_text, S("ab%d" % id(head), 13.5, 21, "KR", INK)))
        body.append(g(10))
    page.append(D.box(body, bg=colors.white, border=CORAL_SOFT, pad=16))
    page.append(g(8))
    page.append(D.PraiseStrip("정답을 확인했어요! 마지막 별도 색칠해 보세요."))
    return page


# ============================================================ 1. 수와 계산 ===
def book1():
    meta = dict(
        doc_title="01 50 이하 수 두 가지 읽기와 여러 가지 덧셈·뺄셈 (유치 6~7세)",
        short="01 수 읽기와 덧셈·뺄셈",
        tag="12월 겨울방학 특강 · 유치 6~7세 · 예비초1",
        title=["수를 두 가지로", "읽고 계산해요"],
        sub="일·이·삼으로도, 하나·둘·셋으로도 읽어 봐요",
        steps=["1~10 두 가지로 읽기", "11~20 두 가지로 읽기",
               "10을 만들어요", "덧셈·뺄셈 놀이", "수수께끼 놀이"],
    )
    pages = []

    # ---------------- 미션 1 ----------------
    p = list(D.mission_head("1", "수를 두 가지 이름으로 읽어요",
                            "같은 수를 부르는 이름이 두 개 있어요."))
    p.append(D.tip_bubble("1은 <b>일</b>이라고도, <b>하나</b>라고도 읽어요.", "선생님 한마디"))
    p.append(g(9))
    p.append(h := D.BigGrid(
        3, 6, cell_h=46,
        values={(0, 0): "수", (0, 1): "1", (0, 2): "2", (0, 3): "3", (0, 4): "4", (0, 5): "5",
                (1, 0): "일", (1, 1): "일", (1, 2): "이", (1, 3): "삼", (1, 4): "사", (1, 5): "오",
                (2, 0): "하나", (2, 1): "하나", (2, 2): "둘", (2, 3): "셋", (2, 4): "넷", (2, 5): "다섯"},
        fills={(1, 0): CREAM_2, (2, 0): CREAM_2, (0, 0): CREAM_2}, font=20))
    p.append(g(14))
    p.append(D.problem_line("1", "6부터 10까지, 두 가지 이름을 써 보세요."))
    p.append(g(4))
    p.append(D.BigGrid(
        3, 6, cell_h=48,
        values={(0, 1): "6", (0, 2): "7", (0, 3): "8", (0, 4): "9", (0, 5): "10",
                (1, 0): "한자어", (2, 0): "고유어"},
        fills={(1, 0): CREAM_2, (2, 0): CREAM_2}, font=18))
    p.append(g(10))
    p.append(g(8))
    p.append(D.problem_line("2", "그림을 세어 보고, 수를 써 보세요."))
    p.append(g(3))
    p.append(D.CountCards([("apple", 3), ("star", 5), ("candy", 4), ("heart", 2)],
                          cols=4, cell_h=96, per_row=3, spacing=21))
    p.append(g(6))
    p.append(D.PraiseStrip("1번 미션 성공! 별에 색칠해 보세요."))
    pages.append(p)

    # ---------------- 미션 2 ----------------
    p = list(D.mission_head("2", "11부터 20까지, 두 가지 이름",
                            "점을 이어서 같은 수를 찾아보세요.", color=MINT, soft=MINT_SOFT))
    p.append(D.problem_line("2", "고유어와 같은 수를 골라 점을 이어 보세요.", color=MINT))
    p.append(g(6))
    p.append(D.ConnectPlay(["열하나", "열둘", "열셋", "열넷"], ["12", "14", "11", "13"], row_h=48))
    p.append(g(12))
    p.append(D.problem_line("3", "빈 칸에 두 가지 이름을 써 보세요.", color=MINT))
    p.append(g(4))
    p.append(D.BigGrid(
        3, 4, cell_h=58,
        values={(0, 0): "수", (0, 1): "15", (0, 2): "18", (0, 3): "20",
                (1, 0): "한자어", (2, 0): "고유어"},
        fills={(1, 0): CREAM_2, (2, 0): CREAM_2, (0, 0): CREAM_2}, font=18))
    p.append(g(10))
    p.append(D.tip_bubble("20은 <b>이십</b>, <b>스물</b>이라고 읽어요. 둘 다 맞아요!", "선생님 한마디"))
    p.append(g(8))
    p.append(D.PraiseStrip("점을 잘 이었어요! 별을 색칠해요."))
    pages.append(p)

    # ---------------- 미션 3 ----------------
    p = list(D.mission_head("3", "10을 만들어요", "두 수를 모아 10을 만들어 봐요.",
                            color=SKY, soft=SKY_SOFT))
    p.append(D.tip_bubble("7 옆에 3이 있으면 10이 돼요. 손가락으로 세어 봐도 좋아요!", "선생님 한마디"))
    p.append(g(10))
    p.append(D.problem_line("4", "□ 안에 알맞은 수를 써 보세요.", color=SKY))
    p.append(g(4))
    p.append(big_cards([("star", "7 + □ = 10"), ("star", "6 + □ = 10"),
                        ("star", "8 + □ = 10"), ("star", "9 + □ = 10")],
                       cols=2, cell_h=96))
    p.append(g(10))
    p.append(D.problem_line("5", "10에서 하나를 빼면 얼마일까요?", color=SKY))
    p.append(g(4))
    p.append(big_cards([("candy", "10 - 3 = □"), ("candy", "10 - 5 = □"),
                        ("candy", "10 - 7 = □"), ("candy", "10 - 9 = □")],
                       cols=2, cell_h=96))
    p.append(g(10))
    p.append(D.PraiseStrip("10을 척척 만들었어요! 별을 색칠해요."))
    pages.append(p)

    # ---------------- 미션 4 ----------------
    p = list(D.mission_head("4", "덧셈·뺄셈 놀이", "사과와 사탕을 세면서 계산해요.",
                            color=PURPLE, soft=PURPLE_SOFT))
    p.append(D.problem_line("6", "계산해 보세요.", color=PURPLE))
    p.append(g(4))
    p.append(big_cards([("apple", "13 + 5 = □"), ("apple", "12 + 7 = □"),
                        ("candy", "15 - 7 = □"), ("candy", "18 - 9 = □")],
                       cols=2, cell_h=100))
    p.append(g(10))
    p.append(D.problem_line("7", "세로셈으로 계산해 보세요.", color=PURPLE))
    p.append(g(4))
    p.append(D.BigVertical([(14, "+", 5), (17, "-", 8)], cell_h=104))
    p.append(g(10))
    p.append(D.PraiseStrip("계산을 잘했어요! 별을 색칠해요."))
    pages.append(p)

    # ---------------- 미션 5 ----------------
    p = list(D.mission_head("5", "수수께끼 놀이", "수를 잘 읽으면 수수께끼도 풀 수 있어요.",
                            color=YELLOW, soft=YELLOW_SOFT))
    p.append(D.problem_line("8", "내가 누구일까요? □ 안에 수를 써 보세요.", color=colors.HexColor("#D9A93F")))
    p.append(g(6))
    rows = [
        "· 나는 <b>스물보다 1 큰 수</b>예요. 나는 ____",
        "· 나는 <b>서른보다 1 작은 수</b>예요. 나는 ____",
        "· 나는 <b>열다섯</b>이라고도, <b>십오</b>라고도 불러요. 나는 ____",
    ]
    body = []
    for r in rows:
        body.append(Paragraph(r, S("q%d" % id(r), 15, 34, "KR", INK)))
    p.append(D.box(body, bg=colors.white, border=YELLOW, pad=14))
    p.append(g(12))
    p.append(D.problem_line("9", "이 수를 두 가지로 읽어 보세요.", color=colors.HexColor("#D9A93F")))
    p.append(g(4))
    p.append(D.BigGrid(
        3, 5, cell_h=54,
        values={(0, 0): "수", (0, 1): "13", (0, 2): "24", (0, 3): "31", (0, 4): "40",
                (1, 0): "한자어", (2, 0): "고유어"},
        fills={(1, 0): CREAM_2, (2, 0): CREAM_2, (0, 0): CREAM_2}, font=18))
    p.append(g(12))
    p.append(D.problem_line("10", "내가 만든 수수께끼를 하나 써 보세요.", color=colors.HexColor("#D9A93F")))
    p.append(g(4))
    p.append(K.DottedLines(2, gap=32, dot=(2.5, 4.5)))
    p.append(g(10))
    p.append(D.PraiseStrip("수수께끼 탐정이 되었어요! 별을 색칠해요."))
    pages.append(p)

    # ---------------- 정답 ----------------
    pages.append(answer_page([
        ("1. 6~10 두 가지 이름",
         "6 육 / 여섯 · 7 칠 / 일곱 · 8 팔 / 여덟 · 9 구 / 아홉 · 10 십 / 열"),
        ("2. 점 잇기",
         "열하나-11 · 열둘-12 · 열셋-13 · 열넷-14"),
        ("3. 빈 칸 채우기",
         "15 십오 / 열다섯 · 18 십팔 / 열여덟 · 20 이십 / 스물"),
        ("4. 10 만들기", "7+3 · 6+4 · 8+2 · 9+1"),
        ("5. 10에서 빼기", "10-3=7 · 10-5=5 · 10-7=3 · 10-9=1"),
        ("6. 계산", "13+5=18 · 12+7=19 · 15-7=8 · 18-9=9"),
        ("7. 세로셈", "14+5=19 · 17-8=9"),
        ("8. 수수께끼", "21(스물하나) · 29(스물아홉) · 15(십오/열다섯)"),
        ("9·10. 두 가지로 읽기 / 내 수수께끼",
         "13 십삼·열셋 · 24 이십사·스물넷 · 31 삼십일·서른하나 · 40 사십·마흔<br/>"
         "아이가 만든 수수께끼는 함께 읽어 주세요. 답이 하나로 정해지면 더 좋아요."),
    ]))
    return D.build(os.path.join(OUT, "01_초1_덧뺄셈_50이하_두가지읽기.pdf"), meta, pages)


# ============================================================ 2. 선과 낱말 ===
def book2():
    meta = dict(
        doc_title="02 교과서 어휘와 문장제 핵심 찾기 (유치 6~7세)",
        short="02 선과 낱말, 문장제",
        tag="12월 겨울방학 특강 · 유치 6~7세 · 예비초1",
        title=["곧은 선, 굽은 선", "낱말을 찾아라"],
        sub="그림을 보고 낱말의 뜻을 알아맞혀요",
        steps=["선의 이름 알기", "탐정처럼 찾아보기", "낱말과 뜻 잇기",
               "필요 없는 말 지우기", "내가 만든 낱말"],
    )
    pages = []

    # ---------------- 미션 1 ----------------
    p = list(D.mission_head("1", "선의 이름을 알아요", "모양마다 부르는 이름이 달라요."))
    p.append(pic_row([("straight", "곧은 선", CORAL), ("curved", "굽은 선", MINT),
                      ("flat", "평평한", SKY), ("bumpy", "울퉁불퉁", PURPLE)], height=112))
    p.append(g(10))
    p.append(D.tip_bubble("<b>곧은 선</b>은 쭉 뻗은 선, <b>굽은 선</b>은 부드럽게 휘어진 선이에요.", "선생님 한마디"))
    p.append(g(10))
    p.append(D.problem_line("1", "말에 맞게 직접 그려 보세요."))
    p.append(g(4))
    rows = [[Paragraph("곧은 선", S("g1", 13, 18, "KRB", CORAL_DEEP)),
             Paragraph("굽은 선", S("g2", 13, 18, "KRB", CORAL_DEEP))], ["", ""]]
    t = Table(rows, [CW / 2, CW / 2], rowHeights=[26, 88])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1.6, colors.HexColor("#E3D3C1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
    ]))
    p.append(t)
    p.append(g(10))
    p.append(D.problem_line("2", "곧은 선과 굽은 선으로 그림을 완성해 보세요."))
    p.append(g(4))
    draw_box = Table([[""]], [CW], rowHeights=[150])
    draw_box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.6, colors.HexColor("#E3D3C1")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
    ]))
    p.append(draw_box)
    p.append(g(4))
    p.append(Paragraph("지붕은 <b>곧은 선</b>, 강은 <b>굽은 선</b>으로 그려 보세요.",
                       S("dhint", 12.5, 18, "KR", GRAY)))
    p.append(g(8))
    p.append(D.PraiseStrip("선 그리기 성공! 별을 색칠해요."))
    pages.append(p)

    # ---------------- 미션 2 ----------------
    p = list(D.mission_head("2", "탐정처럼 찾아보자!", "그림을 잘 보고 말에 맞는 것을 찾아요.",
                            color=MINT, soft=MINT_SOFT))
    p.append(D.problem_line("2", "곧은 선을 찾아 ○, 굽은 선을 찾아 △ 해 보세요.", color=MINT))
    p.append(g(6))
    p.append(pic_row([("bend", "꺾인 선", MINT), ("straight", "쭉 뻗은 선", CORAL),
                      ("curved", "휘어진 선", SKY), ("bumpy", "울퉁불퉁", PURPLE)], height=104))
    p.append(g(8))
    p.append(Paragraph("① ____   ② ____   ③ ____   ④ ____",
                       S("ans2", 17, 26, "KR", INK, 1)))
    p.append(g(12))
    p.append(D.problem_line("3", "평평한 것과 울퉁불퉁한 것을 이어 보세요.", color=MINT))
    p.append(g(6))
    p.append(D.ConnectPlay(["평평한", "울퉁불퉁한"], ["밋밋하고 고른 모양", "오르내리는 모양"], row_h=44))
    p.append(g(10))
    p.append(D.PraiseStrip("탐정처럼 잘 찾았어요! 별을 색칠해요."))
    pages.append(p)

    # ---------------- 미션 3 ----------------
    p = list(D.mission_head("3", "낱말과 뜻을 이어요", "낱말의 뜻을 알고 있는지 확인해요.",
                            color=SKY, soft=SKY_SOFT))
    p.append(D.problem_line("4", "낱말과 뜻을 점으로 이어 보세요.", color=SKY))
    p.append(g(6))
    p.append(D.ConnectPlay(["곧은 선", "굽은 선", "평평한", "울퉁불퉁한"],
                           ["부드럽게 휘어진 선", "높낮이가 고른 모양",
                            "쭉 뻗은 선", "오르내리는 모양"], row_h=46))
    p.append(g(12))
    p.append(D.problem_line("5", "□ 안에 알맞은 낱말을 써 보세요.", color=SKY))
    p.append(g(4))
    qs = ["· 운동장은 넓고 ______ 땅이에요.",
          "· 자로 그은 선은 ______이에요.",
          "· 산은 ______ 모양이에요."]
    body = [Paragraph(q, S("r%d" % id(q), 15, 34, "KR", INK)) for q in qs]
    p.append(D.box(body, bg=colors.white, border=SKY, pad=14))
    p.append(g(10))
    p.append(D.PraiseStrip("낱말 박사가 되었어요! 별을 색칠해요."))
    pages.append(p)

    # ---------------- 미션 4 ----------------
    p = list(D.mission_head("4", "필요 없는 말을 지워요", "문제를 풀 때는 쓰는 말만 남겨요.",
                            color=PURPLE, soft=PURPLE_SOFT))
    p.append(D.tip_bubble("답을 구하는 데 쓰지 않는 말에는 <b>X</b>를 그어요. 남은 수로 식을 만들어요!", "선생님 한마디"))
    p.append(g(10))
    p.append(D.problem_line("6", "문제를 읽고, 필요 없는 말에 X를 그어 보세요.", color=PURPLE))
    p.append(g(6))
    p.append(D.box([Paragraph("민준이는 사과 12개와 귤 7개를 샀어요.<br/>그중 사과 3개를 먹었어요.<br/>"
                              "남은 사과는 몇 개일까요?", S("s1", 16, 28))],
                   bg=colors.white, border=PURPLE, pad=14))
    p.append(g(6))
    p.append(Paragraph("식 : ______________________     답 : ____________",
                       S("e1", 16, 30, "KR", GRAY)))
    p.append(g(10))
    p.append(D.problem_line("7", "이번에는 어떤 말을 지울까요?", color=PURPLE))
    p.append(g(6))
    p.append(D.box([Paragraph("교실에 책상이 18개 있어요.<br/>그중 5개를 1학년 교실로 옮겼어요.<br/>"
                              "교실에 남은 책상은 몇 개일까요?", S("s2", 16, 28))],
                   bg=colors.white, border=PURPLE, pad=14))
    p.append(g(6))
    p.append(Paragraph("식 : ______________________     답 : ____________",
                       S("e2", 16, 30, "KR", GRAY)))
    p.append(g(8))
    p.append(D.PraiseStrip("필요 없는 말을 잘 지웠어요! 별을 색칠해요."))
    pages.append(p)

    # ---------------- 미션 5 ----------------
    p = list(D.mission_head("5", "내가 만든 낱말", "배운 낱말로 짧은 글을 지어 봐요.",
                            color=YELLOW, soft=YELLOW_SOFT))
    p.append(D.problem_line("8", "배운 낱말 3개를 넣어 두 문장을 써 보세요.",
                            color=colors.HexColor("#D9A93F")))
    p.append(g(6))
    p.append(Paragraph("보기 : 운동장은 <b>평평</b>해요. 산은 <b>울퉁불퉁</b>해요.",
                       S("ex5", 13.5, 22, "KR", GRAY)))
    p.append(g(8))
    p.append(K.DottedLines(4, gap=34, dot=(2.5, 4.5)))
    p.append(g(10))
    p.append(D.PraiseStrip("글쓰기 성공! 마지막 별을 색칠해요."))
    pages.append(p)

    pages.append(answer_page([
        ("1. 그려 보기", "곧은 선은 자로 그은 듯 반듯하게, 굽은 선은 부드럽게 휘어 그리면 좋아요."),
        ("2. 찾아 표시하기", "① 꺾인 선 - 곧은 선으로 꺾여 있어요(○) ② ○ ③ △ ④ △"),
        ("3. 이어 보기", "평평한 - 밋밋하고 고른 모양 · 울퉁불퉁한 - 오르내리는 모양"),
        ("4. 낱말과 뜻", "곧은 선 - 쭉 뻗은 선 · 굽은 선 - 부드럽게 휘어진 선 · "
                    "평평한 - 높낮이가 고른 모양 · 울퉁불퉁한 - 오르내리는 모양"),
        ("5. □ 낱말", "평평한 · 곧은 선 · 울퉁불퉁한"),
        ("6. 지울 말", "귤 7개에 X → 12-3=9(개)"),
        ("7. 지울 말", "지울 말이 없어요 → 18-5=13(개)"),
        ("8. 짧은 글", "낱말 3개가 바른 뜻으로 들어 있으면 좋아요."),
    ]))
    return D.build(os.path.join(OUT, "02_초등_교과서어휘_문장제핵심찾기.pdf"), meta, pages)


# ============================================================ 3. 스토리 한자 ===
def book3():
    meta = dict(
        doc_title="03 상형문자 스토리 배경지식 한자 (유치 6~7세)",
        short="03 스토리 한자 탐험",
        tag="12월 겨울방학 특강 · 유치 6~7세 · 예비초1",
        title=["그림이 글자가", "되었어요"],
        sub="스토리 한자 탐험을 떠나 볼까요?",
        steps=["해와 달", "산과 내", "나무와 불", "물과 사람",
               "그림과 글자 연결"],
    )
    pages = []

    def char_page(mission, pairs, color, soft, note=None):
        p = list(D.mission_head(mission[0], mission[1], mission[2], color=color, soft=soft))
        for ch, picto, reading, story in pairs:
            pic = D.PictoBigRow([(picto, "그림", color)], height=112)
            head = Paragraph("<font name='KRS' size='44'>%s</font>" % ch,
                             S("hc%s" % ch, 44, 68, "KRS", NAVY))
            reading_p = Paragraph(reading, S("hr%s" % ch, 17, 23, "KRB", color))
            story_p = Paragraph(story, S("hs%s" % ch, 13.5, 20, "KR", INK))
            card = Table([[pic, head], ["", reading_p], ["", story_p]],
                         colWidths=[116, CW - 116 - 30],
                         rowHeights=[None, 26, None])
            card.setStyle(TableStyle([
                ("SPAN", (0, 0), (0, 2)),
                ("VALIGN", (0, 0), (0, 2), "MIDDLE"),
                ("VALIGN", (1, 0), (1, 0), "BOTTOM"),
                ("VALIGN", (1, 1), (1, 2), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (1, 0), (1, 0), 6),
                ("BOTTOMPADDING", (1, 0), (1, 0), 0),
                ("TOPPADDING", (1, 1), (1, 1), 2),
                ("BOTTOMPADDING", (1, 1), (1, 1), 0),
                ("TOPPADDING", (1, 2), (1, 2), 4),
                ("BOTTOMPADDING", (0, 2), (0, 2), 0),
            ]))
            p.append(D.box([card], bg=colors.white, border=soft, pad=12))
            p.append(g(8))
        if note:
            p.append(D.tip_bubble(note, "이야기 한 조각"))
            p.append(g(8))
        # 따라 쓰기
        p.append(D.problem_line("따", "글자를 네 번씩 따라 써 보세요.", size=16, color=color))
        p.append(g(4))
        rows = []
        for ch, _, reading, _ in pairs:
            rows.append([Paragraph("<font name='KRS' size='20'>%s</font>" % ch, S("t%s" % ch, 18, 26)),
                         Paragraph(reading, S("tr%s" % ch, 11, 16, "KR", GRAY))] + [""] * 4)
        widths = [15 * mm, 20 * mm] + [(CW - 35 * mm) / 4] * 4
        p.append(Table(rows, widths, rowHeights=[44] * len(rows), style=TableStyle([
            ("GRID", (0, 0), (-1, -1), 1.4, colors.HexColor("#E3D3C1")),
            ("BACKGROUND", (0, 0), (0, -1), CREAM_2),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (1, -1), "CENTER"),
        ])))
        p.append(g(10))
        p.append(D.PraiseStrip("한자 탐험 성공! 별을 색칠해요."))
        return p

    pages.append(char_page(
        ("1", "해와 달", "그림이 어떻게 글자가 되었을까요?"),
        [("日", "sun", "해 일", "해의 둥근 모양을 그리고 가운데 점을 찍었어요."),
         ("月", "moon", "달 월", "가느다란 초승달 모양을 그대로 옮겼어요.")],
        CORAL, CORAL_SOFT, "밤이 되면 달이, 아침이 되면 해가 떠요. 둘 다 둥글게 생겼지요!"))

    pages.append(char_page(
        ("2", "산과 내", "산은 뾰족, 물은 줄줄."),
        [("山", "mountain", "뫼 산", "산봉우리 세 개가 솟은 모양이에요."),
         ("川", "river", "내 천", "물이 세 갈래로 흐르는 모양이에요.")],
        MINT, MINT_SOFT, "산에 가면 물이 흐르는 내를 만날 수 있어요."))

    pages.append(char_page(
        ("3", "나무와 불", "나무에서 불이 나요."),
        [("木", "tree", "나무 목", "줄기와 가지, 뿌리를 그린 모양이에요."),
         ("火", "fire", "불 화", "타오르는 불꽃의 모양을 그렸어요.")],
        PURPLE, PURPLE_SOFT, "나무를 문지르면 불이 날 수도 있어요. 옛사람들도 그렇게 불을 피웠대요."))

    pages.append(char_page(
        ("4", "물과 사람", "사람은 두 다리로 서요."),
        [("水", "water", "물 수", "가운데 물줄기와 양옆 물방울을 그렸어요."),
         ("人", "person", "사람 인", "두 다리로 선 사람의 옆모습이에요.")],
        SKY, SKY_SOFT, "물은 소중해요. 아껴 쓰는 습관을 들여요."))

    # ---------------- 미션 5: 그림과 글자 연결 ----------------
    p = list(D.mission_head("5", "그림과 글자를 이어요", "배운 글자를 기억하고 있나요?",
                            color=YELLOW, soft=YELLOW_SOFT))
    p.append(D.problem_line("5", "그림을 보고 알맞은 한자를 써 보세요.",
                            color=colors.HexColor("#D9A93F")))
    p.append(g(6))
    p.append(D.PictoBigRow([("sun", "해 ____", CORAL), ("moon", "달 ____", CORAL),
                            ("tree", "나무 ____", PURPLE), ("person", "사람 ____", SKY)],
                           height=98))
    p.append(g(8))
    p.append(Paragraph("보기 : 日 · 月 · 山 · 川 · 木 · 火 · 水 · 人",
                       S("bogi", 15, 24, "KRB", CORAL_DEEP, 1)))
    p.append(g(12))
    p.append(D.problem_line("6", "한자로 된 낱말의 뜻을 골라 ○ 해 보세요.",
                            color=colors.HexColor("#D9A93F")))
    p.append(g(4))
    body = [Paragraph("<b>日記</b>  ① 일기(하루 기록)   ② 일상", S("w1", 16, 32)),
            Paragraph("<b>山水</b>  ① 산과 물   ② 물고기", S("w2", 16, 32))]
    p.append(D.box(body, bg=colors.white, border=YELLOW, pad=14))
    p.append(g(10))
    p.append(D.PraiseStrip("한자 탐험대장! 별을 색칠해요."))
    pages.append(p)

    pages.append(answer_page([
        ("5. 그림과 글자", "해 日 · 달 月 · 나무 木 · 사람 人"),
        ("6. 낱말의 뜻", "日記 ① · 山水 ①"),
        ("따라 쓰기", "획순을 지켜 천천히 쓰면 글자가 반듯해져요."),
    ]))
    return D.build(os.path.join(OUT, "03_상형문자_스토리_배경지식_한자.pdf"), meta, pages)


# ============================================================ 4. 서술형 ===
def book4():
    meta = dict(
        doc_title="04 서술형 표현 공부 워크시트 (유치 6~7세)",
        short="04 왜 그렇게 생각했어요?",
        tag="12월 겨울방학 특강 · 유치 6~7세 · 예비초1",
        title=["왜 그렇게", "생각했어요?"],
        sub="말로 먼저, 그리고 글로 써 봐요",
        steps=["말풍선으로 말하기", "식과 까닭 쓰기", "한 번 더 연습",
               "문장 늘리기", "내 생각 쓰기"],
    )
    pages = []

    # ---------------- 미션 1 ----------------
    p = list(D.mission_head("1", "말로 먼저 말해 봐요", "네 칸에 차례대로 말해 보세요."))
    p.append(D.tip_bubble("말로 먼저 해 보면 글로 쓸 때 훨씬 쉬워요. 선생님·부모님과 함께 해 보세요!",
                          "선생님 한마디"))
    p.append(g(10))
    steps = [("①", "무엇을 묻나요?", "구하는 것을 찾아요", CORAL_SOFT, CORAL_DEEP),
             ("②", "무엇을 알고 있나요?", "알고 있는 수를 찾아요", MINT_SOFT, MINT),
             ("③", "어떤 식을 세웠나요?", "더하기? 빼기?", SKY_SOFT, SKY),
             ("④", "왜 그렇게 했나요?", "까닭을 말해요", PURPLE_SOFT, PURPLE)]
    for num, q, hint, soft, colr in steps:
        card = Table([[Paragraph("<font color='#FFFFFF'>%s</font>" % num,
                                 S("sn%s" % num, 16, 20, "KRB", colors.white, 1)),
                       [Paragraph(q, S("sq%s" % num, 16, 24, "KRB", colr)),
                        Paragraph(hint, S("sh%s" % num, 12.5, 18, "KR", GRAY))]]],
                     colWidths=[40, CW - 90], rowHeights=[58])
        card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colr),
            ("BACKGROUND", (1, 0), (1, 0), colors.white),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("LEFTPADDING", (1, 0), (1, 0), 12),
            ("BOX", (1, 0), (1, 0), 1.4, colr),
            ("ROUNDEDCORNERS", [10, 10, 10, 10]),
        ]))
        p.append(card)
        p.append(g(7))

    p.append(g(4))
    p.append(D.problem_line("1", "함께 해 보세요. 네 칸에 말해 보고, 소리 내어 따라 읽어요."))
    p.append(g(6))
    p.append(D.box([Paragraph("지호는 구슬을 <b>14개</b> 가지고 있었어요.<br/>"
                              "친구에게 <b>6개</b>를 주었어요.<br/>남은 구슬은 몇 개일까요?",
                              S("q1s", 15, 26))],
                   bg=colors.white, border=CORAL, pad=14))
    p.append(g(8))
    p.append(D.box([Paragraph("<font color='#D9502F'><b>이렇게 말해요</b></font>",
                              S("bb1", 12, 17, "KRB", CORAL_DEEP)),
                    g(2),
                    Paragraph("14개에서 6개를 줬으니까 <b>14-6=8</b>, 남은 구슬은 <b>8개</b>예요!",
                              S("bb2", 15, 24))],
                   bg=YELLOW_SOFT, border=YELLOW, pad=12))
    p.append(g(10))
    p.append(D.PraiseStrip("말로 잘 설명했어요! 별을 색칠해요."))
    pages.append(p)

    # ---------------- 미션 2 ----------------
    def step_card(q_text, color):
        out = [D.problem_line("2", q_text, size=15, color=color), g(6)]
        rows = [[Paragraph("① 무엇을 묻나요?", S("c1", 11.5, 16, "KRB", color)),
                 Paragraph("② 무엇을 알고 있나요?", S("c2", 11.5, 16, "KRB", color))],
                ["", ""],
                [Paragraph("③ 식", S("c3", 11.5, 16, "KRB", color)),
                 Paragraph("④ 왜 그렇게 생각했나요?", S("c4", 11.5, 16, "KRB", color))],
                ["", ""]]
        t = Table(rows, [CW / 2, CW / 2], rowHeights=[16, 96, 16, 140])
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1.4, colors.HexColor("#E3D3C1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (-1, 0), CREAM_2),
            ("BACKGROUND", (0, 2), (-1, 2), CREAM_2),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
        ]))
        out.append(t)
        return out

    p = list(D.mission_head("2", "식과 까닭을 함께 써요", "식을 쓰고, 왜 그런지도 써 보세요.",
                            color=MINT, soft=MINT_SOFT))
    p.extend(step_card("지호는 구슬을 14개 가지고 있었어요. 친구에게 6개를 주었어요. 남은 구슬은 몇 개일까요?", MINT))
    p.append(g(10))
    p.append(D.tip_bubble("까닭을 쓸 때는 <b>~니까</b>, <b>~해서</b>, <b>~때문에</b>를 넣어 보세요.", "쓰기 도움말"))
    p.append(D.PraiseStrip("식을 잘 세웠어요! 별을 색칠해요."))
    pages.append(p)

    # ---------------- 미션 3 ----------------
    p = list(D.mission_head("3", "한 번 더 연습해요", "이번에는 내 힘으로 풀어 봐요.",
                            color=SKY, soft=SKY_SOFT))
    p.extend(step_card("한 봉지에 사탕이 10개씩 있어요. 3봉지를 열었어요. 그중 13개를 먹었어요. 남은 사탕은 몇 개일까요?", SKY))
    p.append(g(10))
    p.append(D.tip_bubble("먼저 <b>모두 몇 개</b>인지 세고, 먹은 만큼 빼면 돼요.", "쓰기 도움말"))
    p.append(D.PraiseStrip("차근차근 잘 풀었어요! 별을 색칠해요."))
    pages.append(p)

    # ---------------- 미션 4 ----------------
    p = list(D.mission_head("4", "문장을 길게 만들어요", "낱말을 더하면 문장이 풍성해져요.",
                            color=PURPLE, soft=PURPLE_SOFT))
    p.append(D.problem_line("4", "짧은 문장을 길게 써 보세요.", color=PURPLE))
    p.append(g(4))
    p.append(Paragraph("보기 : 새가 난다. → 작은 참새가 나뭇가지에서 힘차게 난다.",
                       S("ex4", 13, 21, "KR", GRAY)))
    p.append(g(8))
    for short in ["친구가 웃었다.", "비가 온다."]:
        rows = [[Paragraph(short, S("sh%d" % id(short), 15, 22, "KRB", NAVY))], ["", ], ["", ]]
        t = Table([[Paragraph(short, S("s%d" % id(short), 15, 22, "KRB", NAVY))] + [""] * 3,
                   ["", "", "", ""], ["", "", "", ""]],
                  colWidths=[CW * 0.3, CW * 0.24, CW * 0.24, CW * 0.22], rowHeights=[26, 34, 34])
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 1.4, colors.HexColor("#E3D3C1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("SPAN", (0, 0), (-1, 0)),
            ("SPAN", (0, 1), (-1, 1)),
            ("SPAN", (0, 2), (-1, 2)),
            ("BACKGROUND", (0, 0), (-1, 0), CREAM_2),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        p.append(t)
        p.append(g(8))
    p.append(D.PraiseStrip("문장이 길어졌어요! 별을 색칠해요."))
    pages.append(p)

    # ---------------- 미션 5 ----------------
    p = list(D.mission_head("5", "내 생각을 써요", "오늘 배운 것으로 내 생각을 써 보세요.",
                            color=YELLOW, soft=YELLOW_SOFT))
    p.append(D.problem_line("5", "그림을 그리고, 내 생각을 두 문장으로 써 보세요.",
                            color=colors.HexColor("#D9A93F")))
    p.append(g(6))
    t = Table([[""]], [CW], rowHeights=[150])
    t.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1.6, colors.HexColor("#E3D3C1")),
                           ("BACKGROUND", (0, 0), (-1, -1), colors.white)]))
    p.append(t)
    p.append(g(8))
    p.append(K.DottedLines(5, gap=32, dot=(2.5, 4.5)))
    p.append(g(10))
    p.append(D.PraiseStrip("오늘도 참 잘했어요! 마지막 별을 색칠해요."))
    pages.append(p)

    pages.append(answer_page([
        ("2. 지호의 구슬", "① 묻는 것: 남은 구슬  ② 아는 것: 14개, 6개를 줌<br/>"
                       "③ 식: 14-6=8  ④ 까닭: 6개를 주었으니 빼야 하기 때문이에요. 답 8개"),
        ("3. 사탕", "① 묻는 것: 남은 사탕  ② 아는 것: 한 봉지 10개, 3봉지, 먹은 13개<br/>"
                 "③ 식: 10+10+10=30, 30-13=17  ④ 까닭: 먼저 모두 몇 개인지 세고, 먹은 만큼 뺐어요. 답 17개"),
        ("4. 문장 늘리기", "예) 놀이터에서 친구가 환하게 웃었다. / 아침부터 보슬보슬 비가 온다."),
        ("5. 내 생각", "그림이 있고 두 문장 이상 썼으면 아주 잘했어요. 칭찬해 주세요!"),
    ]))
    return D.build(os.path.join(OUT, "04_서술형_표현공부_워크시트.pdf"), meta, pages)


BUILDERS = {"1": book1, "2": book2, "3": book3, "4": book4}


def main(argv):
    keys = argv[1:] or list(BUILDERS)
    for k in keys:
        print("wrote", BUILDERS[k]())


if __name__ == "__main__":
    main(sys.argv)
