# -*- coding: utf-8 -*-
"""Trich toan bo ky hieu (block) dang dung trong ban ve goc, bay thanh bang mau."""
import sys, math, collections, ezdxf
from ezdxf.addons import Importer
from ezdxf.enums import TextEntityAlignment
from ezdxf import bbox

TEN_MOI = {
    "83fsdfsdffawer23r23r23r": "LC_XA-SVP+DAU-COT-TLD",
    "83DFGDFGRTERT":           "LC_COT-TLD-DZ",
    "83GDFG4TERTWE":           "LC_DE-COT",
    "83A$C1038421F":           "LC_KYHIEU-TRON-3NHANH",
}
src = ezdxf.readfile(sys.argv[1]); smsp = src.modelspace()
dem = collections.Counter(e.dxf.name for e in smsp.query("INSERT"))
ten_dung = [n for n, _ in dem.most_common() if not n.startswith("*")]

doc = ezdxf.new("R2010", setup=True)
doc.styles.add("KCM", font="arial.ttf")
for n, c in [("TV_KYHIEU", 7), ("TV_KHUNG", 8), ("TV_CHU", 2)]:
    if n not in doc.layers: doc.layers.add(n, color=c)
imp = Importer(src, doc); imp.import_blocks(ten_dung); imp.finalize()
msp = doc.modelspace()

O = 4000.0            # buoc o luoi
NCOT = 5
msp.add_text("THU VIEN KY HIEU - MAT CAT A-A LO CHO (trich tu ban ve goc cua Cong ty)",
             height=260, dxfattribs={"layer": "TV_CHU", "style": "KCM"}) \
   .set_placement((0, O*1.2), align=TextEntityAlignment.LEFT)

for i, ten in enumerate(ten_dung):
    moi = TEN_MOI.get(ten)
    if moi and ten in doc.blocks and moi not in doc.blocks:
        doc.blocks.rename_block(ten, moi)
    nb = moi or ten
    cx, cy = (i % NCOT) * O, -(i // NCOT) * O
    tmp = msp.add_blockref(nb, (0, 0))
    try:
        bb = bbox.extents([tmp]); w, h = bb.size.x, bb.size.y
        k = (O * 0.58) / max(w, h, 1.0)
        off = (bb.center.x, bb.center.y)
    except Exception:
        k, off = 1.0, (0.0, 0.0)
    msp.delete_entity(tmp)
    r = msp.add_blockref(nb, (cx - off[0]*k, cy - off[1]*k),
                         dxfattribs={"layer": "TV_KYHIEU", "xscale": k, "yscale": k, "zscale": k})
    msp.add_lwpolyline([(cx-O*0.44, cy-O*0.40), (cx+O*0.44, cy-O*0.40),
                        (cx+O*0.44, cy+O*0.40), (cx-O*0.44, cy+O*0.40)],
                       close=True, dxfattribs={"layer": "TV_KHUNG"})
    nhan = f"{nb}\n(goc: {ten} | dung {dem[ten]} lan | ty le xem {k:.2f})"
    m = msp.add_mtext(nhan, dxfattribs={"layer": "TV_CHU", "style": "KCM", "char_height": 130})
    m.set_location((cx, cy - O*0.47), attachment_point=2)

out = sys.argv[2]; doc.saveas(out)
print("DA XUAT:", out, "| so ky hieu:", len(ten_dung))
for n in ten_dung: print(f"   {TEN_MOI.get(n, n):28s}  <- {n:28s} dung {dem[n]} lan")
