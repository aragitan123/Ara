"""유치 6~7세용 놀이형 워크북 도구 (ReportLab, A4).

큰 글씨·큰 칸·귀여운 도형(별·구름·깃발·연필·말풍선)이 기본값입니다.
기존 pdfkit 위에 얹어 쓰며, 폰트는 pdfkit.register_fonts()가 등록한 것을 그대로 씁니다.
"""
import os
import math

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

import pdfkit as K

# ------------------------------------------------------------------ palette ---
CORAL = colors.HexColor("#EE6B4D")
CORAL_DEEP = colors.HexColor("#D9502F")
CORAL_SOFT = colors.HexColor("#FDE7DE")
NAVY = colors.HexColor("#2A4462")
NAVY_SOFT = colors.HexColor("#E8EFF6")
CREAM = colors.HexColor("#FFF9F1")
CREAM_2 = colors.HexColor("#FDF0DE")
INK = colors.HexColor("#3B332C")
GRAY = colors.HexColor("#7E756C")
LINE = colors.HexColor("#EADCCB")
MINT = colors.HexColor("#57A18B")
MINT_SOFT = colors.HexColor("#E8F4EF")
YELLOW = colors.HexColor("#F7C35C")
YELLOW_SOFT = colors.HexColor("#FFF3D6")
SKY = colors.HexColor("#8CC0DE")
SKY_SOFT = colors.HexColor("#E9F4FA")
PINK = colors.HexColor("#F08BA0")
PINK_SOFT = colors.HexColor("#FDE9ED")
PURPLE = colors.HexColor("#8E7CC3")
PURPLE_SOFT = colors.HexColor("#F0EBFA")

PW, PH = A4
ML = MR = 15 * mm
MT = 22 * mm
MB = 17 * mm
CW = PW - ML - MR
FRAME_H = PH - MT - MB

PALETTE = [(CORAL, CORAL_SOFT), (MINT, MINT_SOFT), (SKY, SKY_SOFT),
           (YELLOW, YELLOW_SOFT), (PURPLE, PURPLE_SOFT), (PINK, PINK_SOFT)]


def st(name, size, leading=None, font="KR", color=INK, align=0, space_before=0, space_after=0):
    return ParagraphStyle(name, fontName=font, fontSize=size,
                          leading=leading or size * 1.45, textColor=color,
                          alignment=align, wordWrap="CJK",
                          spaceBefore=space_before, spaceAfter=space_after)


# 큰 글씨 기본 스타일
S_COVER_TAG = st("c_tag", 16, 22, "KRB", CORAL_DEEP)
S_COVER_TITLE = st("c_title", 34, 46, "KRB", NAVY, 1)
S_COVER_SUB = st("c_sub", 16, 26, "KR", GRAY, 1)
S_MISSION = st("mission", 13, 18, "KRB", colors.white)
S_H1 = st("h1", 25, 34, "KRB", NAVY)
S_H2 = st("h2", 18, 26, "KRB", NAVY)
S_BODY = st("body", 15, 24)
S_BODY_C = st("bodyc", 15, 24, align=1)
S_NOTE = st("note", 12.5, 19, "KR", GRAY)
S_BIG_NUM = st("bnum", 20, 26, "KRB", NAVY, 1)
S_CELL = st("cell", 17, 24, "KR", INK, 1)


# ------------------------------------------------------------------ doodles ---
def star(c, cx, cy, r, fill=None, stroke=None, lw=2, points=5, inner=0.45):
    c.saveState()
    p = c.beginPath()
    for i in range(points * 2):
        ang = -math.pi / 2 + i * math.pi / points
        rad = r if i % 2 == 0 else r * inner
        x, y = cx + math.cos(ang) * rad, cy + math.sin(ang) * rad
        if i == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    p.close()
    if fill:
        c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(lw)
    c.drawPath(p, stroke=1 if stroke else 0, fill=1 if fill else 0)
    c.restoreState()


def heart(c, cx, cy, size, fill=CORAL, stroke=None):
    c.saveState()
    s = size
    p = c.beginPath()
    p.moveTo(cx, cy - s * 0.55)
    p.curveTo(cx - s * 1.1, cy + s * 0.25, cx - s * 0.45, cy + s * 0.95, cx, cy + s * 0.42)
    p.curveTo(cx + s * 0.45, cy + s * 0.95, cx + s * 1.1, cy + s * 0.25, cx, cy - s * 0.55)
    c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(1.6)
    c.drawPath(p, stroke=1 if stroke else 0, fill=1)
    c.restoreState()


def cloud(c, cx, cy, w, fill=colors.white, stroke=K.LINE):
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(1.4)
    r = w / 4.2
    p = c.beginPath()
    p.moveTo(cx - w * 0.45, cy - r * 0.5)
    p.curveTo(cx - w * 0.62, cy + r * 0.9, cx - w * 0.25, cy + r * 1.35, cx - w * 0.05, cy + r * 0.85)
    p.curveTo(cx + w * 0.1, cy + r * 1.7, cx + w * 0.45, cy + r * 1.2, cx + w * 0.35, cy + r * 0.6)
    p.curveTo(cx + w * 0.6, cy + r * 0.55, cx + w * 0.55, cy - r * 0.5, cx + w * 0.4, cy - r * 0.5)
    p.lineTo(cx - w * 0.45, cy - r * 0.5)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def flag(c, x, y, h=26, fill=CORAL):
    c.saveState()
    c.setStrokeColor(colors.HexColor("#B9A894"))
    c.setLineWidth(2)
    c.line(x, y, x, y + h)
    c.setFillColor(fill)
    p = c.beginPath()
    p.moveTo(x, y + h)
    p.lineTo(x + 22, y + h - 7)
    p.lineTo(x, y + h - 14)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()


def pencil(c, x, y, h=34, angle=20):
    c.saveState()
    c.translate(x, y)
    c.rotate(angle)
    w = h * 0.22
    c.setFillColor(YELLOW)
    c.setStrokeColor(colors.HexColor("#D9A93F"))
    c.setLineWidth(1.2)
    c.rect(0, 0, w, h * 0.78, stroke=1, fill=1)
    c.setFillColor(colors.HexColor("#F0D0A8"))
    p = c.beginPath()
    p.moveTo(0, 0)
    p.lineTo(w / 2, -h * 0.16)
    p.lineTo(w, 0)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.setFillColor(CORAL)
    c.rect(0, h * 0.78, w, h * 0.09, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#EFE3D6"))
    c.rect(0, h * 0.87, w, h * 0.13, stroke=1, fill=1)
    c.restoreState()


def sun_face(c, cx, cy, r):
    c.saveState()
    c.setFillColor(YELLOW)
    c.setStrokeColor(colors.HexColor("#E0A93C"))
    c.setLineWidth(1.6)
    for i in range(8):
        ang = i * math.pi / 4
        c.line(cx + math.cos(ang) * r * 1.15, cy + math.sin(ang) * r * 1.15,
               cx + math.cos(ang) * r * 1.5, cy + math.sin(ang) * r * 1.5)
    c.circle(cx, cy, r, stroke=1, fill=1)
    c.setFillColor(colors.HexColor("#8A6A2F"))
    c.circle(cx - r * 0.33, cy + r * 0.16, r * 0.1, stroke=0, fill=1)
    c.circle(cx + r * 0.33, cy + r * 0.16, r * 0.1, stroke=0, fill=1)
    p = c.beginPath()
    p.moveTo(cx - r * 0.3, cy - r * 0.2)
    p.curveTo(cx - r * 0.1, cy - r * 0.5, cx + r * 0.1, cy - r * 0.5, cx + r * 0.3, cy - r * 0.2)
    c.setStrokeColor(colors.HexColor("#8A6A2F"))
    c.setLineWidth(1.8)
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


def apple(c, cx, cy, r, fill=colors.HexColor("#E8604C")):
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(colors.HexColor("#C2452F"))
    c.setLineWidth(1.2)
    c.circle(cx - r * 0.32, cy, r * 0.72, stroke=1, fill=1)
    c.circle(cx + r * 0.32, cy, r * 0.72, stroke=1, fill=1)
    c.setStrokeColor(colors.HexColor("#7A5230"))
    c.setLineWidth(2)
    c.line(cx, cy + r * 0.6, cx + r * 0.12, cy + r * 1.1)
    c.setFillColor(colors.HexColor("#6FA96A"))
    c.setStrokeColor(colors.HexColor("#578A53"))
    p = c.beginPath()
    p.moveTo(cx + r * 0.12, cy + r * 0.95)
    p.curveTo(cx + r * 0.7, cy + r * 1.25, cx + r * 0.8, cy + r * 0.85, cx + r * 0.2, cy + r * 0.75)
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def candy(c, cx, cy, w=26, fill=PINK):
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(colors.HexColor("#D06A80"))
    c.setLineWidth(1.2)
    c.circle(cx, cy, w * 0.28, stroke=1, fill=1)
    p = c.beginPath()
    p.moveTo(cx - w * 0.28, cy)
    p.lineTo(cx - w * 0.55, cy + w * 0.22)
    p.lineTo(cx - w * 0.55, cy - w * 0.22)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    p = c.beginPath()
    p.moveTo(cx + w * 0.28, cy)
    p.lineTo(cx + w * 0.55, cy + w * 0.22)
    p.lineTo(cx + w * 0.55, cy - w * 0.22)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def speech_bubble(c, x, y, w, h, fill=colors.white, stroke=CORAL, lw=1.8):
    c.saveState()
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(lw)
    c.roundRect(x, y, w, h, min(w, h) * 0.28, stroke=1, fill=1)
    p = c.beginPath()
    p.moveTo(x + w * 0.22, y + 2)
    p.lineTo(x + w * 0.16, y - h * 0.28)
    p.lineTo(x + w * 0.42, y + 2)
    c.drawPath(p, stroke=1, fill=1)
    c.setStrokeColor(fill)
    c.setLineWidth(lw + 1)
    c.line(x + w * 0.24, y + 1.5, x + w * 0.4, y + 1.5)
    c.restoreState()


# ----------------------------------------------------------------- flowables ---
class Doodles(Flowable):
    """A thin decorative strip (stars / cloud / flags)."""

    def __init__(self, kind="stars", height=26, color=CORAL):
        super().__init__()
        self.kind = kind
        self.height = height
        self.color = color

    def wrap(self, aw, ah):
        self.w = aw
        return self.w, self.height

    def draw(self):
        c = self.canv
        if self.kind == "stars":
            for i, x in enumerate((0.06, 0.16, 0.26)):
                star(c, self.w * x, self.height / 2, 5.5 + i, fill=YELLOW_SOFT, stroke=YELLOW, lw=1.2)
        elif self.kind == "clouds":
            cloud(c, self.w * 0.15, 6, 60)
            cloud(c, self.w * 0.42, 12, 44)
        elif self.kind == "line":
            star(c, 8, self.height / 2, 6, fill=YELLOW, stroke=None)
            star(c, self.w - 8, self.height / 2, 6, fill=YELLOW, stroke=None)
            c.setStrokeColor(self.color)
            c.setLineWidth(1.2)
            c.setDash(3, 4)
            c.line(18, self.height / 2, self.w - 18, self.height / 2)


class BigGrid(Flowable):
    """큰 칸 격자 — 첫 줄 머리글, 나머지는 쓰기 칸."""

    def __init__(self, rows, cols, cell_h=60, values=None, head=True,
                 label_col=None, border=colors.HexColor("#E3D3C1"),
                 fills=None, font=18, bold_values=True):
        super().__init__()
        self.rows, self.cols = rows, cols
        self.cell_h = cell_h
        self.values = values or {}
        self.head = head
        self.label_col = label_col
        self.border = border
        self.fills = fills or {}
        self.font = font
        self.bold_values = bold_values
        self.height = cell_h * rows

    def wrap(self, aw, ah):
        self.w = aw
        self.cell_w = aw / self.cols
        return self.w, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        for (r, col), colr in self.fills.items():
            c.setFillColor(colr)
            c.rect(col * self.cell_w, self.height - (r + 1) * self.cell_h,
                   self.cell_w, self.cell_h, stroke=0, fill=1)
        if self.head:
            c.setFillColor(NAVY_SOFT)
            c.rect(0, self.height - self.cell_h, self.w, self.cell_h, stroke=0, fill=1)
        if self.label_col:
            c.setFillColor(CREAM_2)
            c.rect(0, 0, self.cell_w, self.height, stroke=0, fill=1)
        c.setStrokeColor(self.border)
        c.setLineWidth(1.4)
        for r in range(self.rows + 1):
            y = self.height - r * self.cell_h
            c.line(0, y, self.w, y)
        for col in range(self.cols + 1):
            x = col * self.cell_w
            c.line(x, 0, x, self.height)
        c.setFillColor(INK)
        for (r, col), v in self.values.items():
            c.setFont("KRB" if self.bold_values else "KR", self.font)
            c.setFillColor(NAVY if self.bold_values else INK)
            c.drawCentredString(col * self.cell_w + self.cell_w / 2,
                                self.height - (r + 0.5) * self.cell_h - self.font * 0.34, str(v))
        c.restoreState()


class ConnectPlay(Flowable):
    """두 줄을 이어 보는 놀이 — 큰 글씨, 둥근 점."""

    def __init__(self, left, right, row_h=44, left_size=18, right_size=18,
                 dot_color=CORAL, marks=True):
        super().__init__()
        self.left, self.right = left, right
        self.row_h = row_h
        self.left_size = left_size
        self.right_size = right_size
        self.dot_color = dot_color
        self.marks = marks

    def wrap(self, aw, ah):
        self.w = aw
        n = max(len(self.left), len(self.right))
        self.height = n * self.row_h + 6
        self.pl = [Paragraph(t, st("cl%d" % i, self.left_size, self.left_size * 1.3, "KRB", NAVY))
                   for i, t in enumerate(self.left)]
        self.pr = [Paragraph(t, st("cr%d" % i, self.right_size, self.right_size * 1.3, "KR", INK, 2))
                   for i, t in enumerate(self.right)]
        return self.w, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        colw = self.w * 0.42
        for i, p in enumerate(self.pl):
            y = self.height - 6 - (i + 0.5) * self.row_h
            _, ph = p.wrap(colw - 26, self.row_h)
            p.drawOn(c, 6, y - ph / 2)
            if self.marks:
                c.setFillColor(self.dot_color)
                c.circle(colw + 8, y + 4, 4.5, stroke=0, fill=1)
        for i, p in enumerate(self.pr):
            y = self.height - 6 - (i + 0.5) * self.row_h
            _, ph = p.wrap(colw - 26, self.row_h)
            p.drawOn(c, self.w - colw + 4, y - ph / 2)
            if self.marks:
                c.setFillColor(self.dot_color)
                c.circle(self.w - colw - 8, y + 4, 4.5, stroke=0, fill=1)
        c.restoreState()


class ItemRow(Flowable):
    """그림 + 큰 식 + 답 칸 3~4개를 한 줄에."""

    def __init__(self, items, cols=4, cell_h=92, idx=True):
        super().__init__()
        self.items = items          # [(kind, value)]  kind: apple/star/candy/none
        self.cols = cols
        self.cell_h = cell_h
        self.idx = idx

    def wrap(self, aw, ah):
        self.w = aw
        self.cell_w = aw / self.cols
        self.rows = math.ceil(len(self.items) / self.cols)
        self.height = self.rows * self.cell_h
        return self.w, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        for i, (kind, text) in enumerate(self.items):
            r, col = divmod(i, self.cols)
            x = col * self.cell_w
            y = self.height - (r + 1) * self.cell_h
            c.setStrokeColor(LINE)
            c.setLineWidth(1.3)
            c.setFillColor(colors.white)
            c.roundRect(x + 4, y + 4, self.cell_w - 8, self.cell_h - 8, 12, stroke=1, fill=1)
            if self.idx:
                c.setFillColor(CORAL_SOFT)
                c.circle(x + 20, y + self.cell_h - 20, 10, stroke=0, fill=1)
                c.setFont("KRB", 11)
                c.setFillColor(CORAL_DEEP)
                c.drawCentredString(x + 20, y + self.cell_h - 24, str(i + 1))
            if kind == "apple":
                apple(c, x + self.cell_w / 2, y + self.cell_h * 0.66, 12)
            elif kind == "star":
                star(c, x + self.cell_w / 2, y + self.cell_h * 0.66, 13, fill=YELLOW_SOFT, stroke=YELLOW, lw=1.6)
            elif kind == "candy":
                candy(c, x + self.cell_w / 2, y + self.cell_h * 0.66, 30)
            c.setFont("KR", 19)
            c.setFillColor(INK)
            c.drawCentredString(x + self.cell_w / 2, y + self.cell_h * 0.40, text)
            c.setStrokeColor(colors.HexColor("#CDBEAD"))
            c.setLineWidth(1.2)
            c.setDash(2, 3)
            c.line(x + self.cell_w * 0.22, y + 22, x + self.cell_w * 0.78, y + 22)
        c.restoreState()


class BigVertical(Flowable):
    """세로셈 큰 칸 — 숫자를 위아래로 놓고 답을 쓰는 공간."""

    def __init__(self, items, cell_h=104, digit_w=24):
        super().__init__()
        self.items = items       # [(a, op, b)]
        self.cell_h = cell_h
        self.digit_w = digit_w
        self.height = cell_h

    def wrap(self, aw, ah):
        self.w = aw
        self.cell_w = aw / len(self.items)
        return self.w, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        for i, (a, op, b) in enumerate(self.items):
            x0 = i * self.cell_w
            c.setFillColor(colors.white)
            c.setStrokeColor(LINE)
            c.setLineWidth(1.4)
            c.roundRect(x0 + 6, 4, self.cell_w - 12, self.cell_h - 8, 12, stroke=1, fill=1)
            digits = max(len(str(a)), len(str(b)))
            right = x0 + self.cell_w / 2 + digits * self.digit_w / 2
            top = self.cell_h - 26
            c.setFont("KR", 23)
            c.setFillColor(INK)
            for k, ch in enumerate(str(a)[::-1]):
                c.drawRightString(right - k * self.digit_w, top, ch)
            for k, ch in enumerate(str(b)[::-1]):
                c.drawRightString(right - k * self.digit_w, top - 32, ch)
            c.setFont("KRB", 20)
            c.setFillColor(CORAL_DEEP)
            c.drawRightString(right - digits * self.digit_w - 3, top - 32, op)
            c.setStrokeColor(NAVY)
            c.setLineWidth(2)
            c.line(right - digits * self.digit_w - 8, top - 40, right + 6, top - 40)
            c.setFillColor(GRAY)
            c.setFont("KR", 9.5)
            c.drawString(x0 + 12, 10, "답")
        c.restoreState()


class CountCards(Flowable):
    """그림을 세어 수를 쓰는 카드 (2열)."""

    def __init__(self, items, cols=2, cell_h=88, per_row=5, spacing=26):
        super().__init__()
        self.items = items      # [(kind, count)]
        self.cols = cols
        self.cell_h = cell_h
        self.per_row = per_row
        self.spacing = spacing

    def wrap(self, aw, ah):
        self.w = aw
        self.cw = aw / self.cols
        self.rows = math.ceil(len(self.items) / self.cols)
        self.height = self.rows * self.cell_h
        return self.w, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        for i, (kind, n) in enumerate(self.items):
            r, col = divmod(i, self.cols)
            x = col * self.cw
            y = self.height - (r + 1) * self.cell_h
            c.setFillColor(colors.white)
            c.setStrokeColor(LINE)
            c.setLineWidth(1.4)
            c.roundRect(x + 6, y + 6, self.cw - 12, self.cell_h - 12, 14, stroke=1, fill=1)
            sc = self.spacing / 26.0
            for k in range(n):
                cx = x + 22 + (k % self.per_row) * self.spacing
                cy = y + self.cell_h - 30 - (k // self.per_row) * 26 * sc
                if kind == "apple":
                    apple(c, cx, cy, 9 * sc)
                elif kind == "star":
                    star(c, cx, cy, 10 * sc, fill=YELLOW_SOFT, stroke=YELLOW, lw=1.4)
                elif kind == "candy":
                    candy(c, cx, cy, 22 * sc)
                elif kind == "heart":
                    heart(c, cx, cy + 1, 7 * sc, fill=PINK_SOFT, stroke=PINK)
            bx = x + self.cw - 56
            c.setStrokeColor(CORAL)
            c.setLineWidth(1.6)
            c.setDash(3, 3)
            c.roundRect(bx, y + 16, 44, self.cell_h - 32, 10, stroke=1, fill=0)
        c.restoreState()


class PraiseStrip(Flowable):
    """페이지 아래 칭찬 별 3개 + 도장 칸."""

    def __init__(self, text="오늘 참 잘했어요! 별에 색칠해 보세요.", height=54):
        super().__init__()
        self.text = text
        self.height = height

    def wrap(self, aw, ah):
        self.w = aw
        self.para = Paragraph(self.text, st("praise", 12.5, 17, "KRB", CORAL_DEEP))
        return self.w, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(CREAM_2)
        c.setStrokeColor(colors.HexColor("#F2D9BE"))
        c.setLineWidth(1.2)
        c.roundRect(0, 0, self.w, self.height - 4, 14, stroke=1, fill=1)
        pw, ph = self.para.wrap(self.w - 150, self.height)
        self.para.drawOn(c, 14, (self.height - 4 - ph) / 2 + 1)
        # 별 3개
        for i in range(3):
            star(c, self.w - 128 + i * 30, (self.height - 4) / 2, 11,
                 fill=colors.white, stroke=YELLOW, lw=2)
        c.setFont("KR", 9.5)
        c.setFillColor(GRAY)
        c.drawRightString(self.w - 12, 5, "완성 도장")
        c.restoreState()


class Box(Flowable):
    """둥근 카드 상자 (파스텔)."""

    def __init__(self, flows, bg=CREAM, border=CORAL, pad=12, radius=16, width=None, top_gap=0):
        super().__init__()
        self.flows = flows
        self.bg = bg
        self.border = border
        self.pad = pad
        self.radius = radius
        self.width = width
        self.top_gap = top_gap

    def wrap(self, aw, ah):
        self.w = self.width or aw
        inner = self.w - self.pad * 2
        h = 0
        for f in self.flows:
            _, fh = f.wrap(inner, ah)
            h += fh
        self.height = h + self.pad * 2
        return self.w, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(self.bg)
        c.setStrokeColor(self.border)
        c.setLineWidth(1.6)
        c.roundRect(0, 0, self.w, self.height, self.radius, stroke=1, fill=1)
        y = self.height - self.pad
        for f in self.flows:
            fw, fh = f.wrap(self.w - self.pad * 2, self.height)
            y -= fh
            f.drawOn(c, self.pad, y)
        c.restoreState()


def box(flows, bg=CREAM, border=CORAL_SOFT, pad=12, radius=16):
    return Box(flows, bg=bg, border=border, pad=pad, radius=radius)


# ------------------------------------------------------------------ sections ---
def mission_head(no, title, subtitle=None, color=CORAL, soft=CORAL_SOFT):
    """미션 배지 + 큰 제목."""
    badge = Paragraph("<font color='#FFFFFF'>오늘의 미션 %s</font>" % no, S_MISSION)
    t = Table([[badge]], colWidths=[88], rowHeights=[24])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("ROUNDEDCORNERS", [12, 12, 12, 12]),
    ]))
    out = [t, Spacer(1, 7)]
    out.append(Paragraph(title, S_H1))
    if subtitle:
        out.append(Spacer(1, 3))
        out.append(Paragraph(subtitle, S_NOTE))
    out.append(Spacer(1, 12))
    return out


def problem_line(no, text, size=17, color=CORAL):
    """동그라미 번호 + 큰 문제 문장."""
    t = Table([[Paragraph("<font color='#FFFFFF'>%s</font>" % no, st("pn", 13, 16, "KRB", colors.white, 1)),
                Paragraph(text, st("pt", size, size * 1.45, "KRB", NAVY))]],
              colWidths=[26, CW - 26])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))
    return t


def tip_bubble(text, title="선생님 한마디"):
    rows = [Paragraph("<font color='#D9502F'><b>%s</b></font>" % title, st("tt", 12.5, 17, "KRB", CORAL_DEEP)),
            Paragraph(text, st("tb", 13, 19.5))]
    return box(rows, bg=YELLOW_SOFT, border=YELLOW, pad=11, radius=14)


def write_lines(n=3, gap=30, dot=(2, 4)):
    return K.DottedLines(n, gap=gap, dot=dot)


# ------------------------------------------------------------------ document ---
class KidDoc(BaseDocTemplate):
    def __init__(self, path, title, short, page_total=None):
        self.short = short
        self.page_no = 0
        BaseDocTemplate.__init__(self, path, pagesize=A4,
                                 leftMargin=ML, rightMargin=MR,
                                 topMargin=MT, bottomMargin=MB,
                                 title=title, author="기탄사고력교실 검단아라학원",
                                 subject="12월 겨울방학 특강 워크북", creator="기탄사고력교실 검단아라학원")
        f = Frame(ML, MB, CW, FRAME_H, id="body", leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
        cf = Frame(ML, MB, CW, FRAME_H, id="cover", leftPadding=0, rightPadding=0,
                   topPadding=0, bottomPadding=0)
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[cf], onPage=self.cover_bg),
            PageTemplate(id="body", frames=[f], onPage=self.header_footer),
        ])

    def cover_bg(self, c, doc):
        c.saveState()
        c.setFillColor(CREAM)
        c.rect(0, 0, PW, PH, stroke=0, fill=1)
        # 위쪽 곡선 띠
        c.setFillColor(CORAL)
        c.rect(0, PH - 26 * mm, PW, 26 * mm, stroke=0, fill=1)
        c.setFillColor(CORAL_SOFT)
        c.circle(-20 * mm, PH - 30 * mm, 26 * mm, stroke=0, fill=1)
        c.setFillColor(YELLOW_SOFT)
        c.circle(PW + 14 * mm, 60 * mm, 44 * mm, stroke=0, fill=1)
        c.setFillColor(SKY_SOFT)
        c.circle(18 * mm, 34 * mm, 22 * mm, stroke=0, fill=1)
        # 장식
        star(c, PW - 34 * mm, PH - 52 * mm, 9, fill=YELLOW, stroke=None)
        star(c, PW - 22 * mm, PH - 66 * mm, 6, fill=YELLOW, stroke=None)
        cloud(c, 30 * mm, PH - 44 * mm, 34 * mm)
        pencil(c, PW - 26 * mm, 92 * mm, 44, angle=-18)
        heart(c, PW - 18 * mm, 130 * mm, 7, fill=PINK)
        c.setFillColor(colors.white)
        c.setFont("KRB", 15)
        c.drawString(ML, PH - 13 * mm, "기탄사고력교실 검단아라학원")
        c.setFont("KR", 11.5)
        c.setFillColor(colors.HexColor("#FFE7DC"))
        c.drawRightString(PW - MR, PH - 13 * mm, "12월 겨울방학 특강")
        c.setFillColor(colors.HexColor("#FFE7DC"))
        c.setFont("KR", 12)
        c.drawString(ML, PH - 21 * mm, "아라역 인근 · 서영아너시티 상가")
        c.restoreState()

    def header_footer(self, c, doc):
        self.page_no += 1
        c.saveState()
        # 헤더
        c.setFillColor(CORAL_SOFT)
        c.roundRect(ML, PH - 16 * mm, CW, 7.6 * mm, 4, stroke=0, fill=1)
        c.setFillColor(CORAL_DEEP)
        c.setFont("KRB", 9.6)
        c.drawString(ML + 7, PH - 13.6 * mm, "기탄사고력교실 검단아라학원")
        c.setFillColor(GRAY)
        c.setFont("KR", 9)
        c.drawRightString(PW - MR - 7, PH - 13.6 * mm, self.short)
        # 푸터
        c.setStrokeColor(LINE)
        c.setLineWidth(1)
        c.setDash(2, 3)
        c.line(ML, 12 * mm, PW - MR, 12 * mm)
        c.setFillColor(GRAY)
        c.setFont("KR", 8.6)
        c.drawString(ML, 8 * mm, "출결·결석 카톡 010-2449-1161  ·  원장 010-2131-1161  ·  @aragitan123")
        c.setFillColor(CORAL_DEEP)
        c.setFont("KRB", 11)
        c.drawRightString(PW - MR, 8 * mm, "%d" % self.page_no)
        c.restoreState()


def cover(meta):
    """표지 구성: meta = dict(tag, title, sub, lines, steps, emoji_doodle)"""
    out = [Spacer(1, 40 * mm)]
    out.append(Paragraph(meta["tag"], st("ct", 15, 22, "KRB", CORAL_DEEP, 1)))
    out.append(Spacer(1, 8))
    for line in meta["title"]:
        out.append(Paragraph(line, st("cti", 33, 44, "KRB", NAVY, 1)))
    out.append(Spacer(1, 8))
    out.append(Paragraph(meta["sub"], st("cs", 15, 25, "KR", GRAY, 1)))
    out.append(Spacer(1, 12))

    # 이름·날짜 카드
    name_row = Table([[Paragraph("이름", st("n", 13, 18, "KRB", CORAL_DEEP)),
                       Paragraph("", st("n2", 13, 18)),
                       Paragraph("날짜", st("n3", 13, 18, "KRB", CORAL_DEEP)),
                       Paragraph("", st("n4", 13, 18))]],
                     colWidths=[16 * mm, 62 * mm, 16 * mm, 52 * mm], rowHeights=[34])
    name_row.setStyle(TableStyle([
        ("LINEBELOW", (1, 0), (1, 0), 1.2, colors.HexColor("#D9C6B2")),
        ("LINEBELOW", (3, 0), (3, 0), 1.2, colors.HexColor("#D9C6B2")),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    out.append(box([name_row], bg=colors.white, border=CORAL_SOFT, pad=14, radius=16))
    out.append(Spacer(1, 14))

    if meta.get("steps"):
        rows = []
        for i, s in enumerate(meta["steps"], 1):
            rows.append([Paragraph("%d" % i, st("st%d" % i, 14, 20, "KRB", colors.white, 1)),
                         Paragraph(s, st("sl%d" % i, 14, 22, "KR", INK))])
        t = Table(rows, colWidths=[12 * mm, CW - 40 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), CORAL),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (1, 0), (1, 0), 8),
        ]))
        out.append(t)
    out.append(Spacer(1, 12))

    return out


def build(path, meta, pages):
    """pages: list of flowable lists; each becomes one page."""
    from reportlab.platypus import KeepTogether
    doc = KidDoc(path, meta["doc_title"], meta["short"])
    story = [NextPageTemplate("body")] + cover(meta)
    for page in pages:
        story.append(PageBreak())
        story.extend(page)
    doc.build(story)
    return path
