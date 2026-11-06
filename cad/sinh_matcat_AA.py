# -*- coding: utf-8 -*-
"""
===========================================================================
 SINH TU DONG: MAT CAT A-A LO CHO  (Cong ty than Duong Huy - TKV)
 Dung lai dung cac block ky hieu lay tu ban ve goc cua Cong ty.
 ---------------------------------------------------------------------
 CACH DUNG: sua cac so trong khoi THONG SO ngay duoi day roi chay lai.
===========================================================================
"""
import math, sys, ezdxf
from ezdxf.addons import Importer
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Matrix44
from ezdxf import bbox

# ========================== THONG SO (SUA O DAY) ==========================
SO_VI          = 19           # so bo vi chong ve tren mat cat
BUOC_COT       = 1000         # buoc xa SVP (1 xa / 2 cot), mm
KHOANG_CACH_COT= 500          # khoang cach giua 2 cot TLD lien ke, mm
GOC_DOC        = 28.0         # goc doc via, do
CHIEU_CAO_LO   = 2228         # chieu cao lo cho (nen -> noc), mm
CHIEU_DAY_VIA  = 3420         # chieu day via ve tren hinh, mm
NHAN_DAY_VIA   = "2500-:-3500"   # chu ghi tren duong kich thuoc day via
CHIEU_DAI_LO   = 40           # chieu dai lo cho, m  (chi de ghi nhan L=)
CUOC_CHAN_THAN = 6            # khoang cach cuoc chan than, m/cuoc
TEN_LO_DUOI    = "Lò DVVT chợ\nTT-9-8(TT)/V9-KTT"
TEN_LO_TREN    = "Lò BXTG chợ\nTT-9-8(TT)/V9-KTT"
GHI_CHU_VI     = "Xà thép SVP + cột TLĐ DZ(22÷28) tiến trước 10m"
TIEU_DE        = "MẶT CẮT:  A - A"
TY_LE          = "1/100"
# ==========================================================================

FILE_GOC = sys.argv[1]
FILE_RA  = sys.argv[2]

# --- Block lay tu ban ve goc: ten goc -> ten moi de hieu ---
BLOCK = {
    "83fsdfsdffawer23r23r23r": "LC_XA-SVP+DAU-COT-TLD",
    "83DFGDFGRTERT":           "LC_COT-TLD-DZ",
    "83GDFG4TERTWE":           "LC_DE-COT",
}
# Offset (tam noi dung - diem chen) do duoc tu ban ve goc, WCS, khi rotation=0
OFFSET = {
    "LC_XA-SVP+DAU-COT-TLD": (-1677044.11, -1251256.09),
    "LC_COT-TLD-DZ":         ( 2182946.82,  -693491.27),
    "LC_DE-COT":             ( 2182960.73,  -693463.53),
}
XSCALE = {"LC_XA-SVP+DAU-COT-TLD": -1.0, "LC_COT-TLD-DZ": 1.0, "LC_DE-COT": 1.0}
# Cao do v (so voi nen lo) va lech pha u, do tu ban ve goc
V_POS  = {"LC_XA-SVP+DAU-COT-TLD": 1087.9, "LC_COT-TLD-DZ": 936.1, "LC_DE-COT": 1076.6}
U_PHA  = {"LC_XA-SVP+DAU-COT-TLD": 0.0,    "LC_COT-TLD-DZ": 0.0,   "LC_DE-COT": -500.0}

BETA = math.radians(28.0)   # goc nghieng san co ben trong block goc, phai bu lai

# ---------------------------------------------------------------- khoi tao
src = ezdxf.readfile(FILE_GOC)
doc = ezdxf.new("R2010", setup=True)
imp = Importer(src, doc)
imp.import_blocks(list(BLOCK.keys()))
imp.finalize()
for old, new in BLOCK.items():
    if old in doc.blocks and new not in doc.blocks:
        doc.blocks.rename_block(old, new)

doc.styles.add("KCM", font="arial.ttf")
LAYERS = [("LC_NEN", 3), ("LC_NOC", 6), ("LC_VIA", 5), ("LC_VICHONG", 7),
          ("LC_KICHTHUOC", 4), ("LC_GHICHU", 2), ("LC_TRUC", 8)]
for n, c in LAYERS:
    if n not in doc.layers:
        doc.layers.add(n, color=c)
DIMST = "KCM-100"
if DIMST not in doc.dimstyles:
    ds = doc.dimstyles.add(DIMST)
    ds.dxf.dimtxsty = "KCM"
for k, v in dict(dimtxt=180, dimasz=120, dimexe=90, dimexo=70, dimgap=60,
                 dimdec=0, dimlfac=1, dimclrt=4, dimclrd=4, dimclre=4,
                 dimtad=1, dimblk="ARCHTICK").items():
    doc.dimstyles.get(DIMST).set_dxf_attrib(k, v)

msp = doc.modelspace()
H   = CHIEU_CAO_LO
DV  = CHIEU_DAY_VIA
U0  = 0.0
LU  = (SO_VI - 1) * BUOC_COT          # chieu dai doan ve vi chong
U_D = U0 - 2500.0                     # dau duoi (lo DVVT)
U_T = U0 + LU + 2500.0                # dau tren (lo BXTG)

# ------------------------------------------------- 1. duong nen / noc / via
msp.add_line((U_D - 1500, 0), (U_T + 1500, 0), dxfattribs={"layer": "LC_NEN"})
msp.add_line((U_D - 1500, -786), (U_T + 1500, -786), dxfattribs={"layer": "LC_NEN"})
msp.add_line((U_D - 1500, H), (U_T + 1500, H), dxfattribs={"layer": "LC_NOC"})
msp.add_line((U_D - 1500, DV), (U_T + 1500, DV), dxfattribs={"layer": "LC_VIA"})
msp.add_line((U_D - 1500, DV + 793), (U_T + 1500, DV + 793), dxfattribs={"layer": "LC_VIA"})

# ------------------------------------------------------- 2. array vi chong
def dat_block(ten, u, v):
    ox, oy = OFFSET[ten]
    cb, sb = math.cos(BETA), math.sin(BETA)
    rx, ry = ox * cb - oy * sb, ox * sb + oy * cb     # xoay offset theo BETA
    msp.add_blockref(ten, (u - rx, v - ry), dxfattribs={
        "layer": "LC_VICHONG", "rotation": math.degrees(BETA),
        "xscale": XSCALE[ten], "yscale": 1.0})

for i in range(SO_VI):
    u = U0 + i * BUOC_COT
    for ten in ("LC_XA-SVP+DAU-COT-TLD", "LC_COT-TLD-DZ", "LC_DE-COT"):
        dat_block(ten, u + U_PHA[ten], V_POS[ten])

# ----------------------------------------------- 2b. cot thuy luc don (ve net)
#  So lieu lay tu ban ve goc: than cot v=99..877, ty cot v=956..1665,
#  ban rong than 120 mm, ty 112 mm, khoa cot o v=877..956.
def ve_cot(u):
    def hcn(x1, y1, x2, y2):
        msp.add_lwpolyline([(x1,y1),(x2,y1),(x2,y2),(x1,y2)], close=True,
                           dxfattribs={"layer": "LC_VICHONG"})
    hcn(u-60, 99,  u+60, 877)      # than cot
    hcn(u-80, 877, u+80, 956)      # khoa cot
    hcn(u-56, 956, u+56, 1665)     # ty cot
N_COT = int(LU / KHOANG_CACH_COT) + 1
for k in range(N_COT):
    ve_cot(U0 + k * KHOANG_CACH_COT)

# chuoi kich thuoc khoang cach cot 500
for k in range(N_COT - 1):
    d = msp.add_linear_dim(base=(0, 2650), p1=(U0+k*KHOANG_CACH_COT, 0),
                           p2=(U0+(k+1)*KHOANG_CACH_COT, 0), dimstyle=DIMST,
                           dxfattribs={"layer": "LC_KICHTHUOC"})
    d.render()

# ------------------------------------------------------- 3. kich thuoc buoc
def dim_ngang(x1, x2, y, text=None):
    d = msp.add_linear_dim(base=(0, y), p1=(x1, 0), p2=(x2, 0),
                           dimstyle=DIMST, text=text or "<>",
                           dxfattribs={"layer": "LC_KICHTHUOC"})
    d.render(); return d
for i in range(SO_VI - 1):
    dim_ngang(U0 + i * BUOC_COT, U0 + (i + 1) * BUOC_COT, -900)
dim_ngang(U0, U0 + LU, -2100, text=f"L={CHIEU_DAI_LO}m")

d = msp.add_linear_dim(base=(U_D - 900, 0), p1=(U_D - 300, 0), p2=(U_D - 300, DV),
                       angle=90, dimstyle=DIMST, text=NHAN_DAY_VIA,
                       dxfattribs={"layer": "LC_KICHTHUOC"})
d.render()
d = msp.add_linear_dim(base=(U_T + 900, 0), p1=(U_T + 300, 0), p2=(U_T + 300, H),
                       angle=90, dimstyle=DIMST, text="<>",
                       dxfattribs={"layer": "LC_KICHTHUOC"})
d.render()

# ------------------------------------------------------------- 4. ghi chu
def ghi(txt, x, y, h=200, align=TextEntityAlignment.MIDDLE_LEFT):
    m = msp.add_mtext(txt, dxfattribs={"layer": "LC_GHICHU", "style": "KCM",
                                       "char_height": h})
    m.set_location((x, y)); return m

ghi(TEN_LO_DUOI, U_D - 2200, -3400)
ghi(TEN_LO_TREN, U_T - 1000, DV + 1300)
ghi(GHI_CHU_VI,  U0 + LU * 0.52, DV + 1300)

n_cuoc = max(1, int(LU / (CUOC_CHAN_THAN * 1000)))
for k in range(1, n_cuoc + 1):
    xc = U0 + k * (LU / (n_cuoc + 1))
    msp.add_line((xc, 0), (xc + 700, -1100), dxfattribs={"layer": "LC_GHICHU"})
    msp.add_line((xc + 700, -1100), (xc + 1400, -1100), dxfattribs={"layer": "LC_GHICHU"})
    ghi(f"Cược chắn than\nsole {CUOC_CHAN_THAN}m/cược", xc + 1500, -1100, h=170)

t = msp.add_mtext(f"{TIEU_DE}\n{TY_LE}",
                  dxfattribs={"layer": "LC_GHICHU", "style": "KCM", "char_height": 320})
t.set_location((U0 + LU / 2, DV + 3000), attachment_point=5)

# --------------------------------------------- 5. xoay ca ban ve theo goc doc
m = Matrix44.z_rotate(math.radians(-GOC_DOC))
for e in msp:
    try: e.transform(m)
    except Exception: pass

doc.saveas(FILE_RA)
e = bbox.extents(msp)
print(f"DA SINH: {FILE_RA}")
print(f"  so vi chong = {SO_VI} | buoc = {BUOC_COT} mm | goc doc = {GOC_DOC}°")
print(f"  chieu dai doan ve = {LU/1000:.1f} m | nhan L = {CHIEU_DAI_LO} m")
print(f"  kich thuoc ban ve = {e.size.x:.0f} x {e.size.y:.0f} mm")
