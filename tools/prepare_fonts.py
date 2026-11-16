"""Noto Sans CJK KR (OTF, CFF) -> subset TTF so ReportLab can embed it.

ReportLab cannot embed PostScript/CFF outlines, so we subset the system Noto
Sans/Serif CJK KR fonts to the characters the worksheets need and convert the
remaining CFF outlines to quadratic (glyf) outlines with cu2qu.
"""
import os
import sys

from fontTools import subset
from fontTools.ttLib import TTFont as FTFont
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

HANGUL = "".join(chr(c) for c in range(0xAC00, 0xD7A4))
HANJA = (
    "日月山川木火水人上下中大小天地雨雪風雲石土田力女子男目耳口手足心"
    "花草林森本末米羊牛馬鳥魚虫貝車門家犬豕虎鹿泉谷岩出入左右前後"
    "東西南北春夏秋冬朝夕明暗多少高低長短新古生死敎學校工夫文章言語"
    "問答讀書筆紙姓名先生父母兄弟姊妹內外間時間分秒年月曜記"
    "一二三四五六七八九十百千萬億"
    "歌訓話數圖音樂體德社會國語算術生"
    "江海湖島空求安全和幸福愛友情"
    "市道邑面洞里村輛船舶飛機場院園室堂殿樓塔窓壁屋"
    "暑寒溫熱冷涼濕乾燥霜露氷凍結溶"
    "兄姉弟婦夫妻兒童子老若幼"
    "始終半部分集別同異舊正誤善惡美醜"
    "表裏近遠稱氏句節聲色形相畵畫"
    "食飮茶飯肉菜果甘辛咸苦酸味香臭"
    "衣服衫履巾冠帶紐房床机椅席"
    "猫甲羽毛角尾爪沙泥岸波流"
    "光影燈電星"
    "族祖孫"
    "晝夜昨週"
    "動走立坐臥見聞寫唱奏遊休睡起"
    "思感情意志望好嫌喜怒哀樂恐驚"
    "計量加減乘除倍答解式題"
)
SYMBOLS = (
    "！？.,·…~～—–-()[]{}<>《》「」『』〈〉【】"
    "+-=×÷±≠≤≥∞√%‰°′″※→←↑↓↔⇒⇔★☆○●◎◇◆□■△▲▽▼▷◁"
    "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
    "‘’“”" '"'
    "＿_|/\\^:;!?@#$&*"
    "ＡＢＣＤＥＦ"
)
ASCII = "".join(chr(c) for c in range(0x20, 0x7F))


def build_charset():
    # Full CJK Unified Ideographs (basic block) so any hanja a worksheet needs
    # is present; the subset keeps the file size reasonable.
    cjk = "".join(chr(c) for c in range(0x4E00, 0xA000))
    chars = set(HANGUL + HANJA + SYMBOLS + ASCII + cjk)
    chars.add("\u00a0")
    chars.add("\u3000")
    return chars


def convert(src, dst, chars):
    opts = subset.Options()
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.name_legacy = True
    opts.notdef_outline = True
    opts.recalc_bounds = True
    opts.drop_tables += ["DSIG"]

    font = subset.load_font(src, opts)
    subsetter = subset.Subsetter(options=opts)
    subsetter.populate(unicodes=[ord(c) for c in chars])
    subsetter.subset(font)
    font.save(dst + ".subset.otf")

    sub = FTFont(dst + ".subset.otf")
    glyph_order = sub.getGlyphOrder()
    glyph_set = sub.getGlyphSet()
    glyf = {}
    for name in glyph_order:
        pen = TTGlyphPen(glyph_set)
        glyph = glyph_set[name]
        glyph.draw(Cu2QuPen(pen, 1.0, reverse_direction=True))
        glyf[name] = pen.glyph()

    sub["loca"] = __import__("fontTools.ttLib.tables._l_o_c_a", fromlist=["table__l_o_c_a"]).table__l_o_c_a()
    sub["glyf"] = __import__("fontTools.ttLib.tables._g_l_y_f", fromlist=["table__g_l_y_f"]).table__g_l_y_f()
    sub["glyf"].glyphs = glyf
    sub["glyf"].glyphOrder = glyph_order
    sub["head"].glyf = sub["glyf"]
    sub["head"].indexToLocFormat = 0
    if "CFF " in sub:
        del sub["CFF "]
    if "VORG" in sub:
        del sub["VORG"]
    if "post" in sub:
        sub["post"].formatType = 2.0
        sub["post"].glyphOrder = glyph_order
        sub["post"].extraNames = []
        sub["post"].mapping = {}
    sub.sfntVersion = "\000\001\000\000"
    glyfTable = sub["glyf"]
    for name in glyph_order:
        glyfTable[name].recalcBounds(glyfTable)
    maxp = sub["maxp"]
    maxp.tableVersion = 0x00010000
    maxp.numGlyphs = len(glyph_order)
    maxp.maxZones = 1
    maxp.maxTwilightPoints = 0
    maxp.maxStorage = 0
    maxp.maxFunctionDefs = 0
    maxp.maxInstructionDefs = 0
    maxp.maxStackElements = 0
    maxp.maxSizeOfInstructions = 0
    maxp.maxComponentElements = 0
    maxp.maxComponentDepth = 0
    maxp.maxPoints = 0
    maxp.maxContours = 0
    maxp.maxCompositePoints = 0
    maxp.maxCompositeContours = 0
    maxp.recalc(sub)
    sub.save(dst)
    os.remove(dst + ".subset.otf")
    return dst


def main():
    chars = build_charset()
    print("charset size:", len(chars))
    jobs = [
        ("/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf", "NotoSansKR-Regular.ttf"),
        (os.path.join(OUT, "NotoSansCJKkr-Bold.otf"), "NotoSansKR-Bold.ttf"),
        ("/usr/share/fonts/pickle-hwp/NotoSerifCJKkr-Regular.otf", "NotoSerifKR-Regular.ttf"),
    ]
    os.makedirs(OUT, exist_ok=True)
    for src, name in jobs:
        dst = os.path.join(OUT, name)
        convert(src, dst, chars)
        print("wrote", dst, os.path.getsize(dst))


if __name__ == "__main__":
    main()
