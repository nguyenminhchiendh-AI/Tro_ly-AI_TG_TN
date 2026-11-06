# -*- coding: utf-8 -*-
"""
=============================================================================
 KEO DAI / RUT NGAN MAT CAT A-A LO CHO  -  Cong ty than Duong Huy (TKV)
 -----------------------------------------------------------------------
 Khong ve lai bat cu thu gi. Cong cu lay chinh ban ve goc cua Cong ty roi:
   1) cat ban ve tai mot vi tri giua doan lap,
   2) day toan bo phan phia tren ra xa / keo lai gan,
   3) nhan ban dung so bo vi chong can them vao cho trong.
 => Moi chi tiet, net ve, ky hieu, khung ten giu nguyen 100%.
 -----------------------------------------------------------------------
 CACH DUNG:  python keodai_lo_cho.py <ban_ve_goc.dxf> <ban_ve_moi.dxf> <so_vi_them>
   so_vi_them > 0 : keo dai them (moi vi = 1 buoc 1000 mm)
   so_vi_them < 0 : rut ngan bot
=============================================================================
"""
import sys, math, ezdxf
from ezdxf import bbox

# ---------------- thong so khung toa do cua ban ve goc (da do duoc) --------
GOC_DOC = -28.0                      # huong truc lo cho, do
O       = (1771875.0, -491085.0)     # goc toa do tren duong nen lo
BUOC    = 1000.0                     # buoc lap cua vi chong, mm
U_CAT   = 20698.0                    # vi tri cat (nam giua doan lap)
# ---------------------------------------------------------------------------

TH = math.radians(GOC_DOC)
UX, UY = math.cos(TH), math.sin(TH)

def u_of(x, y):
    return (x - O[0]) * UX + (y - O[1]) * UY

def dich(p, d):
    """Doi diem p di d mm doc theo truc lo cho."""
    return (p[0] + d * UX, p[1] + d * UY)

SRC, DST = sys.argv[1], sys.argv[2]
N_THEM   = int(sys.argv[3])
DL       = N_THEM * BUOC

doc = ezdxf.readfile(SRC)
msp = doc.modelspace()

# ------------------------------------------------- phan loai & keo gian ----
DIEM = ("CIRCLE", "ARC", "ELLIPSE", "TEXT", "MTEXT", "INSERT", "POINT",
        "ATTDEF", "SHAPE", "IMAGE", "SOLID", "3DFACE", "TRACE")

def diem_dai_dien(e):
    """Diem dac trung cua entity dang 'khoi' -> quyet dinh di hay o."""
    t = e.dxftype()
    if t in ("CIRCLE", "ARC", "ELLIPSE"): p = e.dxf.center
    elif t == "MTEXT":                    p = e.dxf.insert
    elif t in ("TEXT", "ATTDEF", "POINT", "SHAPE"): p = e.dxf.insert if t != "POINT" else e.dxf.location
    else:
        try:
            bb = bbox.extents([e])
            if not bb.has_data: return None
            p = bb.center
        except Exception: return None
    return (p.x, p.y)

def keo_gian(e, trong_block_dim=False):
    """Keo gian 1 entity theo quy tac: dinh nao co u >= U_CAT thi dich DL."""
    t = e.dxftype()
    if t == "LINE":
        for attr in ("start", "end"):
            p = e.dxf.get(attr)
            if u_of(p.x, p.y) >= U_CAT:
                np_ = dich((p.x, p.y), DL); e.dxf.set(attr, (np_[0], np_[1], p.z))
        return
    if t == "LWPOLYLINE":
        pts = list(e.get_points("xyseb"))
        out = []
        for x, y, s, b, bu in pts:
            if u_of(x, y) >= U_CAT: x, y = dich((x, y), DL)
            out.append((x, y, s, b, bu))
        e.set_points(out, format="xyseb"); return
    if t == "POLYLINE":
        for v in e.vertices:
            p = v.dxf.location
            if u_of(p.x, p.y) >= U_CAT:
                np_ = dich((p.x, p.y), DL); v.dxf.location = (np_[0], np_[1], p.z)
        return
    if t == "LEADER":
        out = []
        for v in list(e.vertices):
            x, y, z = (v.x, v.y, v.z) if hasattr(v, "x") else (v[0], v[1], v[2] if len(v) > 2 else 0.0)
            if u_of(x, y) >= U_CAT: x, y = dich((x, y), DL)
            out.append((x, y, z))
        e.set_vertices(out); return
    if t == "SPLINE":
        pts = [(p.x, p.y, p.z) for p in e.control_points]
        e.control_points = [dich((x, y), DL) + (z,) if u_of(x, y) >= U_CAT else (x, y, z)
                            for x, y, z in pts]
        if e.fit_points:
            fp = [(p.x, p.y, p.z) for p in e.fit_points]
            e.fit_points = [dich((x, y), DL) + (z,) if u_of(x, y) >= U_CAT else (x, y, z)
                            for x, y, z in fp]
        return
    if t == "HATCH":
        for path in e.paths:
            if path.type.name == "POLYLINE":
                path.vertices = [(dich((v[0], v[1]), DL) + (v[2],))[:3] if u_of(v[0], v[1]) >= U_CAT
                                 else v for v in path.vertices]
            else:
                for ed in getattr(path, "edges", []):
                    for a in ("start", "end", "center"):
                        v = getattr(ed, a, None)
                        if v is not None and u_of(v[0], v[1]) >= U_CAT:
                            setattr(ed, a, dich((v[0], v[1]), DL))
        return
    if t == "WIPEOUT":
        # mat na trang: chi dich khi nam tron ben kia duong cat, neu vat qua thi de yen
        try:
            bb = bbox.extents([e])
            cs = [(bb.extmin.x, bb.extmin.y), (bb.extmax.x, bb.extmax.y),
                  (bb.extmin.x, bb.extmax.y), (bb.extmax.x, bb.extmin.y)]
            us = [u_of(*c) for c in cs]
            if min(us) >= U_CAT:
                e.translate(DL * UX, DL * UY, 0)
        except Exception: pass
        return
    if t == "DIMENSION":
        # 1) cac diem dinh nghia
        for attr in ("defpoint", "defpoint2", "defpoint3", "defpoint4", "defpoint5", "text_midpoint"):
            if e.dxf.hasattr(attr):
                p = e.dxf.get(attr)
                if u_of(p.x, p.y) >= U_CAT:
                    np_ = dich((p.x, p.y), DL); e.dxf.set(attr, (np_[0], np_[1], p.z))
        # 2) hinh ve thuc te nam trong block an danh *D..
        gb = e.dxf.get("geometry", None)
        if gb and gb in doc.blocks:
            for se in doc.blocks[gb]:
                keo_gian(se, True)
        return
    # con lai: entity dang khoi -> di nguyen con
    p = diem_dai_dien(e)
    if p and u_of(p[0], p[1]) >= U_CAT:
        try: e.translate(DL * UX, DL * UY, 0)
        except Exception: pass

# ------------------------------- dac trung cua entity: (u giua, be rong theo u)
def dac_trung(e):
    t = e.dxftype(); us = []
    if t == "LINE":
        us = [u_of(e.dxf.start.x, e.dxf.start.y), u_of(e.dxf.end.x, e.dxf.end.y)]
    elif t == "LWPOLYLINE":
        us = [u_of(x, y) for x, y in e.get_points("xy")]
    elif t == "POLYLINE":
        us = [u_of(v.dxf.location.x, v.dxf.location.y) for v in e.vertices]
    if us:
        return (us[0] + us[-1]) / 2 if len(us) < 3 else (min(us) + max(us)) / 2, max(us) - min(us)
    try:
        bb = bbox.extents([e])
        if not bb.has_data: return None
        cs = [(bb.extmin.x, bb.extmin.y), (bb.extmax.x, bb.extmax.y),
              (bb.extmin.x, bb.extmax.y), (bb.extmax.x, bb.extmin.y)]
        uu = [u_of(*c) for c in cs]
        return u_of(bb.center.x, bb.center.y), max(uu) - min(uu)
    except Exception:
        return None

CUC_BO = 3.0 * BUOC      # be rong toi da de coi la chi tiet cuc bo (lap lai)

# ---- RUT NGAN: xoa bot cac bo vi chong truoc khi don phan dau tren lai gan ----
if N_THEM < 0:
    n_xoa = 0
    for e in list(msp):
        r = dac_trung(e)
        if r and r[1] <= CUC_BO and (U_CAT + DL) <= r[0] < U_CAT:
            try: msp.delete_entity(e); n_xoa += 1
            except Exception: pass
    print(f"  Da xoa {n_xoa} doi tuong ung voi {-N_THEM} bo vi chong")

# ---- KEO DAI: ghi nho mot chu ky mau TRUOC khi keo gian ----
mau = []
if N_THEM > 0:
    A, B = U_CAT - BUOC, U_CAT
    for e in list(msp):
        r = dac_trung(e)
        if r and r[1] <= CUC_BO and A <= r[0] < B:
            mau.append(e)
    print(f"  Chu ky mau u=[{A:.0f},{B:.0f}] co {len(mau)} doi tuong")

# ---- keo gian toan bo ban ve ----
if DL != 0:
    for e in list(msp):
        keo_gian(e)

# ---- KEO DAI: nhan ban chu ky mau vao cho trong ----
for k in range(max(0, N_THEM)):
    d = (k + 1) * BUOC
    for e in mau:
        try:
            ne = e.copy(); msp.add_entity(ne); ne.translate(d * UX, d * UY, 0)
        except Exception:
            pass

# ---------------------------------------- cap nhat nhan chieu dai tong L=
NHAN_L = sys.argv[4] if len(sys.argv) > 4 else None
if NHAN_L:
    for e in msp.query("DIMENSION"):
        try: m = e.get_measurement()
        except Exception: continue
        if m and m > 10000:
            e.dxf.text = "{\\H1.875x;" + NHAN_L + "}"
            gb = e.dxf.get("geometry", None)
            if gb and gb in doc.blocks:
                for se in doc.blocks[gb]:
                    if se.dxftype() == "MTEXT": se.text = NHAN_L
                    elif se.dxftype() == "TEXT": se.dxf.text = NHAN_L
            print(f"  Da doi nhan chieu dai tong -> {NHAN_L}")

doc.saveas(DST)
ext = bbox.extents(msp, fast=True)
print(f"DA XUAT: {DST}")
print(f"  so vi them = {N_THEM}  ({DL/1000:+.0f} m)")
print(f"  kich thuoc ban ve: {ext.size.x:.0f} x {ext.size.y:.0f} mm")
