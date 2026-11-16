"""Small layout toolkit for the 검단아라학원 worksheet PDFs (ReportLab, A4).

Everything is drawn with ReportLab so the output is true vector text with the
noto/nanum Korean fonts embedded (no glyph substitution, printable at any size).
"""
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable, Frame,
                                KeepTogether, PageBreak, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(os.path.dirname(HERE), "fonts")

# ---------------------------------------------------------------- palette ----
CORAL = colors.HexColor("#DE5B3C")
CORAL_SOFT = colors.HexColor("#FBE7DF")
CORAL_LINE = colors.HexColor("#F0B9A5")
NAVY = colors.HexColor("#20364F")
NAVY_SOFT = colors.HexColor("#E6ECF2")
CREAM = colors.HexColor("#FFF8F0")
CREAM_DEEP = colors.HexColor("#FBEFE2")
INK = colors.HexColor("#2A2A2A")
GRAY = colors.HexColor("#6E6A66")
LINE = colors.HexColor("#E2D6CA")
MINT = colors.HexColor("#3F7D6B")
MINT_SOFT = colors.HexColor("#E4F0EB")

PAGE_W, PAGE_H = A4
M_LEFT = M_RIGHT = 17 * mm
M_TOP = 26 * mm
M_BOTTOM = 20 * mm
CONTENT_W = PAGE_W - M_LEFT - M_RIGHT

CFG = {}

# ------------------------------------------------------------------ fonts ----
def register_fonts():
    if getattr(register_fonts, "_done", False):
        return
    pdfmetrics.registerFont(TTFont("KR", os.path.join(FONT_DIR, "NotoSansKR-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("KRB", os.path.join(FONT_DIR, "NotoSansKR-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("KRL", os.path.join(FONT_DIR, "NotoSansKR-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("KRS", os.path.join(FONT_DIR, "NotoSerifKR-Regular.ttf")))
    pdfmetrics.registerFontFamily("KR", normal="KR", bold="KRB", italic="KR", boldItalic="KRB")
    pdfmetrics.registerFontFamily("KRS", normal="KRS", bold="KRB", italic="KRS", boldItalic="KRB")
    for alias in ("KRB", "KRL"):
        pdfmetrics.registerFontFamily(alias, normal=alias, bold=alias, italic=alias, boldItalic=alias)
    register_fonts._done = True


def S(**kw):
    """Paragraph style helper with Korean-friendly CJK wrapping."""
    base = dict(fontName="KR", fontSize=10, leading=16, textColor=INK,
                wordWrap="CJK", spaceBefore=0, spaceAfter=0)
    base.update(kw)
    return ParagraphStyle(name=kw.pop("name", "s%d" % id(kw)), **base)


STY = {}


def styles():
    if STY:
        return STY
    STY.update({
        "cover_tag": S(fontName="KRB", fontSize=10.5, leading=14, textColor=CORAL),
        "cover_title": S(fontName="KRS", fontSize=30, leading=40, textColor=NAVY),
        "cover_sub": S(fontName="KR", fontSize=12.5, leading=20, textColor=GRAY),
        "h1": S(fontName="KRB", fontSize=21, leading=28, textColor=NAVY),
        "h2": S(fontName="KRB", fontSize=13.5, leading=19, textColor=NAVY),
        "h3": S(fontName="KRB", fontSize=11, leading=16, textColor=CORAL),
        "body": S(fontSize=10, leading=17),
        "body_j": S(fontSize=10, leading=17, alignment=TA_JUSTIFY),
        "small": S(fontSize=8.8, leading=14, textColor=GRAY),
        "tiny": S(fontSize=7.8, leading=11.5, textColor=GRAY),
        "note": S(fontSize=9, leading=15, textColor=NAVY),
        "tip": S(fontSize=9, leading=15, textColor=MINT),
        "cell": S(fontSize=10, leading=15, alignment=TA_CENTER),
        "cell_l": S(fontSize=10, leading=15, alignment=TA_LEFT),
        "num": S(fontName="KRB", fontSize=11.5, leading=15, textColor=CORAL),
        "white": S(fontSize=10, leading=15, textColor=colors.white),
        "white_b": S(fontName="KRB", fontSize=10, leading=15, textColor=colors.white),
    })
    return STY


P = lambda text, style="body": Paragraph(text, styles()[style])


register_fonts()


# ------------------------------------------------------------- flowables ----
class Rule(Flowable):
    def __init__(self, width=None, color=LINE, thickness=0.7, space_before=0, space_after=0, dash=None):
        super().__init__()
        self.w = width if width is not None else CONTENT_W
        self.color = color
        self.th = thickness
        self.sb = space_before
        self.sa = space_after
        self.dash = dash
        self.height = thickness + space_before + space_after

    def wrap(self, aw, ah):
        self.w = min(self.w, aw)
        return self.w, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(self.color)
        c.setLineWidth(self.th)
        if self.dash:
            c.setDash(self.dash)
        y = self.sa
        c.line(0, y, self.w, y)
        c.restoreState()


class DottedLines(Flowable):
    """Answer lines with a light dotted rule."""

    def __init__(self, count=2, gap=15, indent=0, width=None, dot=(1.2, 3.2)):
        super().__init__()
        self.count = count
        self.gap = gap
        self.indent = indent
        self.w = width
        self.dot = dot
        self.height = count * gap

    def wrap(self, aw, ah):
        self.w = min(self.w or aw, aw)
        return self.w, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(colors.HexColor("#CFC3B7"))
        c.setLineWidth(0.6)
        c.setDash(self.dot[0], self.dot[1])
        for i in range(self.count):
            y = self.height - (i + 1) * self.gap + 4
            c.line(self.indent, y, self.w - 2, y)
        c.restoreState()


class WriteGrid(Flowable):
    """A writing grid (rows x cols) with optional numbers pre-filled."""

    def __init__(self, rows, cols, cell_w=None, cell_h=20, values=None,
                 label=None, fill_color=None, bold_values=True, border=colors.HexColor("#D9CCC0")):
        super().__init__()
        self.rows, self.cols = rows, cols
        self.cell_w = cell_w
        self.cell_h = cell_h
        self.values = values or {}
        self.label = label
        self.fill_color = fill_color
        self.bold_values = bold_values
        self.border = border
        self.height = rows * cell_h

    def wrap(self, aw, ah):
        self.cell_w = self.cell_w or (aw / self.cols)
        self.w = self.cell_w * self.cols
        return self.w, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        if self.fill_color:
            c.setFillColor(self.fill_color)
            c.rect(0, 0, self.w, self.height, stroke=0, fill=1)
        c.setStrokeColor(self.border)
        c.setLineWidth(0.7)
        for r in range(self.rows + 1):
            y = self.height - r * self.cell_h
            c.line(0, y, self.w, y)
        for col in range(self.cols + 1):
            x = col * self.cell_w
            c.line(x, 0, x, self.height)
        c.setFillColor(INK)
        for (r, col), v in self.values.items():
            fnt = "KRB" if self.bold_values else "KR"
            c.setFont(fnt, 10)
            c.setFillColor(NAVY if self.bold_values else INK)
            c.drawCentredString(col * self.cell_w + self.cell_w / 2,
                                self.height - r * self.cell_h - self.cell_h / 2 - 3.4, str(v))
        c.restoreState()


class ConnectCols(Flowable):
    """Two columns of items with round marks for drawing connecting lines."""

    def __init__(self, left, right, height=None, left_style=None, right_style=None,
                 mark="o", gap=None, row_h=24):
        super().__init__()
        self.left, self.right = left, right
        self.h = height
        self.left_style = left_style or S(fontSize=10.5, leading=14)
        self.right_style = right_style or S(fontSize=10.5, leading=14, alignment=TA_RIGHT)
        self.mark = mark
        self.row_h = row_h

    def wrap(self, aw, ah):
        n = max(len(self.left), len(self.right))
        self.h = self.h or n * self.row_h + 6
        self.w = aw
        self._paras_l = [Paragraph(t, self.left_style) for t in self.left]
        self._paras_r = [Paragraph(t, self.right_style) for t in self.right]
        return self.w, self.h

    def draw(self):
        c = self.canv
        c.saveState()
        col_w = self.w * 0.40
        n = max(len(self.left), len(self.right))
        step = (self.h - 8) / max(n, 1)
        c.setFillColor(colors.HexColor("#A9A29B"))
        c.setStrokeColor(colors.HexColor("#A9A29B"))
        for i, para in enumerate(self._paras_l):
            y = self.h - 8 - (i + 0.5) * step
            _, ph = para.wrap(col_w - 18, step)
            para.drawOn(c, 0, y - ph / 2)
            c.circle(col_w + 2, y + 3, 2.2, stroke=0, fill=1)
        for i, para in enumerate(self._paras_r):
            y = self.h - 8 - (i + 0.5) * step
            _, ph = para.wrap(col_w - 18, step)
            para.drawOn(c, self.w - col_w, y - ph / 2)
            c.circle(self.w - col_w - 8, y + 3, 2.2, stroke=0, fill=1)
        c.restoreState()


def draw_picto(c, kind, x, y, w, h, color=CORAL, lw=3.2, alpha=1.0):
    """Draw a simple pictograph (갑골문 느낌) inside the box (x, y, w, h)."""
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(lw)
    c.setLineCap(1)
    c.setLineJoin(1)
    cx, cy = x + w / 2, y + h / 2
    s = min(w, h) * 0.34
    c.setFillAlpha(alpha)
    if kind == "sun":
        c.circle(cx, cy, s, stroke=1, fill=0)
        c.circle(cx, cy, s * 0.16, stroke=0, fill=1)
        c.line(cx, cy + s * 1.25, cx, cy + s * 1.5)
        c.line(cx, cy - s * 1.25, cx, cy - s * 1.5)
        c.line(cx + s * 1.25, cy, cx + s * 1.5, cy)
        c.line(cx - s * 1.25, cy, cx - s * 1.5, cy)
    elif kind == "moon":
        p = c.beginPath()
        p.moveTo(cx + s * 0.55, cy + s * 0.95)
        p.curveTo(cx - s * 0.75, cy + s * 0.9, cx - s * 0.75, cy - s * 0.9, cx + s * 0.55, cy - s * 0.95)
        p.curveTo(cx - s * 0.15, cy - s * 0.45, cx - s * 0.15, cy + s * 0.45, cx + s * 0.55, cy + s * 0.95)
        c.drawPath(p, stroke=1, fill=0)
    elif kind == "mountain":
        for dx, hh in ((-s, s * 0.95), (0, s * 1.35), (s, s * 0.95)):
            p = c.beginPath()
            p.moveTo(cx + dx - s * 0.75, cy - s * 0.75)
            p.lineTo(cx + dx, cy + hh - s * 0.75)
            p.lineTo(cx + dx + s * 0.75, cy - s * 0.75)
            c.drawPath(p, stroke=1, fill=0)
    elif kind == "river":
        c.line(cx - s * 0.85, cy + s, cx - s * 0.85, cy - s)
        c.line(cx, cy + s * 1.15, cx, cy - s * 1.15)
        c.line(cx + s * 0.85, cy + s, cx + s * 0.85, cy - s)
    elif kind == "tree":
        c.line(cx, cy - s * 1.1, cx, cy + s * 1.1)
        c.line(cx - s * 0.8, cy + s * 0.5, cx + s * 0.8, cy + s * 0.5)
        c.line(cx - s * 0.6, cy - s * 0.2, cx + s * 0.6, cy - s * 0.2)
        for dx in (-0.55, 0.55):
            c.line(cx + dx * s, cy - s * 0.2, cx + dx * s * 1.5, cy - s * 0.75)
    elif kind == "fire":
        p = c.beginPath()
        p.moveTo(cx, cy - s)
        p.curveTo(cx - s * 0.95, cy - s * 0.2, cx - s * 0.3, cy + s * 0.95, cx, cy + s * 1.05)
        p.curveTo(cx + s * 0.3, cy + s * 0.95, cx + s * 0.95, cy - s * 0.2, cx, cy - s)
        c.drawPath(p, stroke=1, fill=0)
        c.line(cx - s * 1.05, cy - s * 0.35, cx - s * 1.05, cy + s * 0.55)
        c.line(cx + s * 1.05, cy - s * 0.35, cx + s * 1.05, cy + s * 0.55)
    elif kind == "water":
        c.line(cx, cy - s * 1.15, cx, cy + s * 1.15)
        for i, yy in enumerate((0.72, 0.24, -0.24, -0.72)):
            off = s * (0.62 if i % 2 == 0 else 0.42)
            c.line(cx - off - s * 0.22, cy + s * yy, cx - off + s * 0.1, cy + s * yy)
            c.line(cx + off - s * 0.1, cy + s * yy, cx + off + s * 0.22, cy + s * yy)
    elif kind == "person":
        c.line(cx - s * 0.55, cy - s * 1.05, cx, cy + s * 0.35)
        c.line(cx + s * 0.55, cy - s * 1.05, cx, cy + s * 0.35)
    elif kind == "up":
        c.line(cx - s, cy - s * 0.15, cx + s, cy - s * 0.15)
        c.line(cx - s * 0.3, cy + s * 0.85, cx + s * 0.3, cy + s * 0.85)
        c.line(cx, cy + s * 0.85, cx, cy - s * 0.15)
    elif kind == "down":
        c.line(cx - s, cy + s * 0.15, cx + s, cy + s * 0.15)
        c.line(cx - s * 0.3, cy - s * 0.85, cx + s * 0.3, cy - s * 0.85)
        c.line(cx, cy + s * 0.15, cx, cy - s * 0.85)
    elif kind == "flat":
        c.line(cx - s * 1.3, cy + s * 0.55, cx + s * 1.3, cy + s * 0.55)
        c.line(cx - s * 1.3, cy - s * 0.35, cx + s * 1.3, cy - s * 0.35)
        c.line(cx - s * 1.3, cy + s * 0.55, cx - s * 1.3, cy - s * 0.35)
        c.line(cx + s * 1.3, cy + s * 0.55, cx + s * 1.3, cy - s * 0.35)
    elif kind == "curved":
        p = c.beginPath()
        p.moveTo(cx - s * 1.25, cy - s * 0.5)
        p.curveTo(cx - s * 0.4, cy + s * 1.1, cx + s * 0.4, cy + s * 1.1, cx + s * 1.25, cy - s * 0.5)
        c.drawPath(p, stroke=1, fill=0)
    elif kind == "hills":
        p = c.beginPath()
        p.moveTo(cx - s * 1.35, cy - s * 0.5)
        p.curveTo(cx - s * 1.05, cy + s * 0.15, cx - s * 0.95, cy + s * 1.0, cx - s * 0.55, cy + s * 1.0)
        p.curveTo(cx - s * 0.2, cy + s * 1.0, cx - s * 0.15, cy + s * 0.1, cx + s * 0.05, cy - s * 0.15)
        p.curveTo(cx + s * 0.3, cy - s * 0.45, cx + s * 0.45, cy + s * 0.95, cx + s * 0.85, cy + s * 0.95)
        p.curveTo(cx + s * 1.15, cy + s * 0.95, cx + s * 1.2, cy + s * 0.1, cx + s * 1.35, cy - s * 0.5)
        c.drawPath(p, stroke=1, fill=0)
    elif kind == "straight":
        c.line(cx - s * 1.3, cy, cx + s * 1.3, cy)
    elif kind == "bend":
        p = c.beginPath()
        p.moveTo(cx - s * 1.2, cy - s * 0.8)
        p.lineTo(cx + s * 0.2, cy - s * 0.8)
        p.lineTo(cx + s * 0.2, cy + s * 0.8)
        c.drawPath(p, stroke=1, fill=0)
    elif kind == "pointy":
        p = c.beginPath()
        p.moveTo(cx - s * 1.2, cy - s * 0.8)
        p.lineTo(cx, cy + s)
        p.lineTo(cx + s * 1.2, cy - s * 0.8)
        c.drawPath(p, stroke=1, fill=0)
    elif kind == "round":
        c.circle(cx, cy, s * 1.05, stroke=1, fill=0)
    elif kind == "bumpy":
        p = c.beginPath()
        p.moveTo(cx - s * 1.35, cy - s * 0.35)
        pts = [(-1.1, 0.55), (-0.85, -0.35), (-0.55, 0.15), (-0.3, -0.35),
               (0.0, 0.75), (0.3, -0.35), (0.6, 0.2), (0.85, -0.35), (1.1, 0.5), (1.35, -0.35)]
        for dx, dy in pts:
            p.lineTo(cx + dx * s, cy + dy * s)
        c.drawPath(p, stroke=1, fill=0)
    c.restoreState()


class PictoRow(Flowable):
    """A row of pictograph cards: picture -> hanja, with a caption."""

    def __init__(self, items, card_w=None, card_h=74, gap=8, show_char=True,
                 bg=CREAM, border=CORAL_LINE, char_style=None):
        super().__init__()
        self.items = items          # list of dicts: {picto, char, name}
        self.card_w = card_w
        self.card_h = card_h
        self.gap = gap
        self.show_char = show_char
        self.bg = bg
        self.border = border
        self.height = card_h

    def wrap(self, aw, ah):
        n = len(self.items)
        self.card_w = self.card_w or (aw - self.gap * (n - 1)) / n
        self.w = self.card_w * n + self.gap * (n - 1)
        return self.w, self.height

    def draw(self):
        c = self.canv
        c.saveState()
        for i, it in enumerate(self.items):
            x = i * (self.card_w + self.gap)
            c.setFillColor(self.bg)
            c.setStrokeColor(self.border)
            c.setLineWidth(1)
            c.roundRect(x, 0, self.card_w, self.card_h, 8, stroke=1, fill=1)
            if self.show_char:
                draw_picto(c, it["picto"], x + 4, self.card_h * 0.30, self.card_w / 2 - 6, self.card_h * 0.55)
                if it.get("char"):
                    c.setFont("KRS", 26)
                    c.setFillColor(NAVY)
                    c.drawCentredString(x + self.card_w * 0.72, self.card_h * 0.40, it["char"])
            else:
                draw_picto(c, it["picto"], x + 6, self.card_h * 0.22, self.card_w - 12, self.card_h * 0.55)
            if it.get("name"):
                c.setFont("KRB", 8.6)
                c.setFillColor(CORAL)
                c.drawCentredString(x + self.card_w / 2, 11, it["name"])
        c.restoreState()


class CheckLine(Flowable):
    """A statement with a trailing checkbox pair (O / X)."""

    def __init__(self, text, style=None, box=13, gap=6, mark_labels=("O", "X")):
        super().__init__()
        self.text = text
        self.style = style or S(fontSize=10, leading=15)
        self.box = box
        self.gap = gap
        self.labels = mark_labels

    def wrap(self, aw, ah):
        self.text_w = aw - (self.box * 2 + self.gap * 3 + 8)
        self.para = Paragraph(self.text, self.style)
        pw, ph = self.para.wrap(self.text_w, 400)
        self.height = max(ph, self.box) + 6
        self.w = aw
        return self.w, self.height

    def draw(self):
        c = self.canv
        para = self.para
        para.drawOn(c, 0, self.height - para.height - 1)
        c.saveState()
        c.setStrokeColor(colors.HexColor("#B9ADA2"))
        c.setFillColor(GRAY)
        c.setLineWidth(0.8)
        c.setFont("KR", 8.6)
        x0 = self.w - (self.box * 2 + self.gap * 2 + 4)
        for i, lab in enumerate(self.labels):
            x = x0 + i * (self.box + self.gap)
            y = self.height - self.box - 2
            c.roundRect(x, y, self.box, self.box, 2.5, stroke=1, fill=0)
            c.drawCentredString(x + self.box / 2, y - 8, lab)
        c.restoreState()


# ------------------------------------------------------------- containers ----
def box(flowables, bg=CREAM, border=CORAL_LINE, pad=9, radius=8, width=None, padding_top=None):
    """Wrap flowables in a rounded light container."""
    t = Table([[flowables]], colWidths=[width or CONTENT_W])
    style = [
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.9, border),
        ("LEFTPADDING", (0, 0), (-1, -1), pad + 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad + 2),
        ("TOPPADDING", (0, 0), (-1, -1), padding_top if padding_top is not None else pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROUNDEDCORNERS", [radius, radius, radius, radius]),
    ]
    t.setStyle(TableStyle(style))
    return t


def section(no, title, sub=None):
    """Section header: coral pill with number + serif title + optional sub."""
    s = styles()
    head = Table(
        [[Paragraph("<font color='#FFFFFF'>%s</font>" % no, s["white_b"]), Paragraph(title, s["h2"])]],
        colWidths=[21, CONTENT_W - 21])
    head.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), CORAL),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("TOPPADDING", (0, 0), (0, 0), 1), ("BOTTOMPADDING", (0, 0), (0, 0), 2),
        ("LEFTPADDING", (1, 0), (1, 0), 8),
        ("TOPPADDING", (1, 0), (1, 0), 0), ("BOTTOMPADDING", (1, 0), (1, 0), 0),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    out = [head]
    if sub:
        out.append(Spacer(1, 3))
        out.append(Paragraph(sub, s["small"]))
    out.append(Spacer(1, 7))
    return out


def problem(no, text, style="body", gap=5, label_w=16):
    """Numbered problem statement."""
    s = styles()
    t = Table([[Paragraph("%s" % no, s["num"]), Paragraph(text, s[style])]],
              colWidths=[label_w, CONTENT_W - label_w])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), gap),
    ]))
    return t


def table(rows, widths, header=True, header_bg=NAVY, header_color=colors.white,
          body_style=None, row_h=None, zebra=None, align="CENTER", font_size=9.5,
          grid_color=LINE, padding=5):
    t = Table(rows, colWidths=widths, rowHeights=row_h)
    st = [
        ("GRID", (0, 0), (-1, -1), 0.6, grid_color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), padding),
        ("RIGHTPADDING", (0, 0), (-1, -1), padding),
        ("TOPPADDING", (0, 0), (-1, -1), padding),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
    ]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), header_bg),
               ("TEXTCOLOR", (0, 0), (-1, 0), header_color),
               ("FONTNAME", (0, 0), (-1, 0), "KRB"),
               ("FONTSIZE", (0, 0), (-1, 0), font_size),
               ("ALIGN", (0, 0), (-1, 0), "CENTER")]
    if zebra:
        for r in range(1 if header else 0, len(rows)):
            if (r % 2 == 0) == zebra:
                st.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#FDF6EE")))
    if body_style:
        st += body_style
    t.setStyle(TableStyle(st))
    return t


def kv_card(rows, width=None, label_bg=CREAM_DEEP):
    """Two-column label/value card used for the rule summaries."""
    s = styles()
    data = [[Paragraph(k, s["h3"]), Paragraph(v, s["body"])] for k, v in rows]
    t = Table(data, colWidths=[(width or CONTENT_W) * 0.30, (width or CONTENT_W) * 0.70])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), label_bg),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


# ---------------------------------------------------------------- document ----
class Doc(BaseDocTemplate):
    def __init__(self, path, meta, **kw):
        self.meta = meta
        self.page_no = 0
        BaseDocTemplate.__init__(self, path, pagesize=A4,
                                 leftMargin=M_LEFT, rightMargin=M_RIGHT,
                                 topMargin=M_TOP, bottomMargin=M_BOTTOM,
                                 title=meta.get("title_plain") or meta["title"],
                                 author="기탄사고력교실 검단아라학원",
                                 subject="12월 겨울방학 특강 학습지",
                                 creator="기탄사고력교실 검단아라학원",
                                 **kw)
        frame = Frame(M_LEFT, M_BOTTOM, CONTENT_W, PAGE_H - M_TOP - M_BOTTOM, id="body",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        cover_frame = Frame(M_LEFT, M_BOTTOM + 6, CONTENT_W, PAGE_H - M_TOP - M_BOTTOM, id="cover",
                            leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[cover_frame], onPage=self.draw_cover_bg),
            PageTemplate(id="body", frames=[frame], onPage=self.draw_header_footer),
        ])

    def draw_cover_bg(self, canv, doc):
        canv.saveState()
        canv.setFillColor(CREAM)
        canv.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        # top coral band
        canv.setFillColor(CORAL)
        canv.rect(0, PAGE_H - 13 * mm, PAGE_W, 13 * mm, stroke=0, fill=1)
        canv.setFillColor(NAVY)
        canv.rect(0, PAGE_H - 15.4 * mm, PAGE_W, 2.4 * mm, stroke=0, fill=1)
        # decorative circles
        canv.setFillColor(colors.HexColor("#F7E2D6"))
        canv.circle(PAGE_W - 22 * mm, 40 * mm, 30 * mm, stroke=0, fill=1)
        canv.setFillColor(colors.HexColor("#FBF0E6"))
        canv.circle(16 * mm, 26 * mm, 22 * mm, stroke=0, fill=1)
        canv.setFillColor(colors.white)
        canv.setFont("KRB", 9)
        canv.drawString(M_LEFT, PAGE_H - 9 * mm, "기탄사고력교실 검단아라학원  ·  12월 겨울방학 특강")
        canv.setFillColor(colors.HexColor("#FFE6DA"))
        canv.setFont("KR", 8)
        canv.drawRightString(PAGE_W - M_RIGHT, PAGE_H - 9 * mm, "아라역 인근 서영아너시티 상가")
        canv.restoreState()

    def draw_header_footer(self, canv, doc):
        self.page_no += 1
        canv.saveState()
        canv.setStrokeColor(CORAL)
        canv.setLineWidth(2.2)
        canv.line(M_LEFT, PAGE_H - 16 * mm, M_LEFT + 16 * mm, PAGE_H - 16 * mm)
        canv.setFillColor(NAVY)
        canv.setFont("KRB", 8.2)
        canv.drawString(M_LEFT, PAGE_H - 20.5 * mm, "기탄사고력교실 검단아라학원")
        canv.setFillColor(GRAY)
        canv.setFont("KR", 7.8)
        canv.drawRightString(PAGE_W - M_RIGHT, PAGE_H - 20.5 * mm,
                             "12월 겨울방학 특강 · %s" % self.meta.get("short_title", ""))
        canv.setStrokeColor(LINE)
        canv.setLineWidth(0.6)
        canv.line(M_LEFT, PAGE_H - 22.6 * mm, PAGE_W - M_RIGHT, PAGE_H - 22.6 * mm)
        # footer
        canv.setStrokeColor(LINE)
        canv.line(M_LEFT, 14 * mm, PAGE_W - M_RIGHT, 14 * mm)
        canv.setFillColor(GRAY)
        canv.setFont("KR", 7.4)
        canv.drawString(M_LEFT, 10 * mm, "출결·결석 카톡 010-2449-1161   |   원장 문의 010-2131-1161   |   @aragitan123")
        canv.setFont("KRB", 8)
        canv.setFillColor(CORAL)
        canv.drawRightString(PAGE_W - M_RIGHT, 10 * mm, "%d" % self.page_no)
        canv.restoreState()


def cover_story(meta):
    s = styles()
    out = [Spacer(1, 16 * mm)]
    out.append(Paragraph(meta["tag"], s["cover_tag"]))
    out.append(Spacer(1, 6))
    out.append(Paragraph(meta["title"], s["cover_title"]))
    out.append(Spacer(1, 8))
    out.append(Paragraph(meta["sub"], s["cover_sub"]))
    out.append(Spacer(1, 14))
    out.append(Rule(width=38 * mm, color=CORAL, thickness=2.4))
    out.append(Spacer(1, 16))
    out.append(Paragraph(meta["intro"], s["body_j"]))
    out.append(Spacer(1, 12))
    if meta.get("goals"):
        rows = [[Paragraph("<font color='#DE5B3C'>●</font> " + g, s["body"])] for g in meta["goals"]]
        out.append(box([Table(rows, colWidths=[CONTENT_W - 30], style=TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ]))], bg=colors.white, border=CORAL_LINE, pad=11))
    out.append(Spacer(1, 16))
    # name / date write-in
    name_line = Table(
        [[Paragraph("이름", s["h3"]), Paragraph("", s["body"]), Paragraph("날짜", s["h3"]), Paragraph("", s["body"])]],
        colWidths=[12 * mm, (CONTENT_W - 12 * mm - 12 * mm - 34 * mm) / 2, 12 * mm,
                   (CONTENT_W - 12 * mm - 12 * mm - 34 * mm) / 2])
    name_line.setStyle(TableStyle([
        ("LINEBELOW", (1, 0), (1, 0), 0.7, colors.HexColor("#C9BCAF")),
        ("LINEBELOW", (3, 0), (3, 0), 0.7, colors.HexColor("#C9BCAF")),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    out.append(name_line)
    if meta.get("steps"):
        out.append(Spacer(1, 16))
        out.append(Paragraph("이 학습지의 순서", s["h3"]))
        out.append(Spacer(1, 5))
        rows = []
        for i, st in enumerate(meta["steps"], 1):
            rows.append([Paragraph("%02d" % i, S(fontName="KRB", fontSize=9, textColor=CORAL)),
                         Paragraph(st, s["small"])])
        tb = Table(rows, colWidths=[10 * mm, CONTENT_W - 10 * mm])
        tb.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        out.append(tb)
    out.append(Spacer(1, 10))
    out.append(Paragraph("이 학습지는 학원 홈페이지 자료실에서 다시 받으실 수 있습니다.",
                         S(fontSize=8, textColor=colors.HexColor("#9A8F86"))))
    out.append(Spacer(1, 9 * mm))
    info = Table([[
        Paragraph("<font color='#DE5B3C'>운영 시간</font><br/>월~목 14:00 ~ 18:30", s["small"]),
        Paragraph("<font color='#DE5B3C'>출결·결석</font><br/>카톡 010-2449-1161", s["small"]),
        Paragraph("<font color='#DE5B3C'>원장 문의</font><br/>010-2131-1161", s["small"]),
        Paragraph("<font color='#DE5B3C'>인스타그램</font><br/>@aragitan123", s["small"]),
    ]], colWidths=[CONTENT_W / 4] * 4)
    info.setStyle(TableStyle([
        ("LINEBEFORE", (1, 0), (-1, -1), 0.6, colors.HexColor("#E7D6C7")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    out.append(info)
    return out


def build_with_cover(path, meta, story):
    """Render cover + content pages with running header/footer."""
    from reportlab.platypus import NextPageTemplate
    doc = Doc(path, meta)
    flow = [NextPageTemplate("body")] + cover_story(meta) + [PageBreak()] + list(story)
    doc.build(flow)
    return path
