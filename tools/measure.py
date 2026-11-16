"""Print the used height of each page of a worksheet story (for layout tuning)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_pdfs as B
import pdfkit as K
from reportlab.platypus import PageBreak

FRAME_H = K.PAGE_H - K.M_TOP - K.M_BOTTOM

def measure(story):
    pages, cur = [], []
    for f in story:
        if isinstance(f, PageBreak):
            pages.append(cur); cur = []
        else:
            cur.append(f)
    pages.append(cur)
    out = []
    for i, page in enumerate(pages):
        used = 0
        for f in page:
            try:
                w, h = f.wrap(K.CONTENT_W, FRAME_H)
            except Exception as e:
                h = 0
            used += h
        out.append((i, round(used), round(FRAME_H - used)))
    return out

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "1"
    fn = getattr(B, "pdf_0" + which)
    # rebuild story without writing: monkeypatch build
    captured = {}
    orig = K.build_with_cover
    def cap(path, meta, story):
        captured["story"] = story
        return path
    K.build_with_cover = cap
    B.K.build_with_cover = cap
    fn()
    for i, used, left in measure(captured["story"][3:] if False else captured["story"]):
        print("page", i, "used", used, "left", left)
    print("frame height", round(FRAME_H))
