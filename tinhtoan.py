# -*- coding: utf-8 -*-
"""
Các hàm tính toán kỹ thuật thông gió - khí mỏ - thoát nước.

Toàn bộ phép tính trong file này do Python thực hiện, KHÔNG do AI tính nhẩm.
Mỗi hàm trả về kèm chuỗi công thức đã dùng để người kiểm tra đối chiếu được.
"""

from dataclasses import dataclass, field


@dataclass
class KetQua:
    ten: str
    gia_tri: float
    don_vi: str
    cong_thuc: str
    dien_giai: str = ""
    canh_bao: list = field(default_factory=list)
    # True khi gia tri da pha vo mot nguong an toan hoac mot yeu cau bat buoc.
    # Giao dien dua vao day de to do o ket qua thay vi to xanh.
    vuot_nguong: bool = False

    def tom_tat(self) -> str:
        trang_thai = "KHONG DAT" if self.vuot_nguong else "Dat"
        dong = [f"{self.ten}: {self.gia_tri:,.2f} {self.don_vi} [{trang_thai}]",
                f"Công thức: {self.cong_thuc}"]
        if self.dien_giai:
            dong.append(self.dien_giai)
        dong.extend(f"CẢNH BÁO: {c}" for c in self.canh_bao)
        return "\n".join(dong)


# ---------------------------------------------------------------- THÔNG GIÓ

def gio_theo_ch4(q_ch4, c_cho_phep, c_gio_vao=0.0, k_du_phong=1.4):
    """Lưu lượng gió cần thiết để pha loãng khí mêtan thoát ra.

    q_ch4        : lưu lượng CH4 tuyệt đối thoát ra (m3/phút)
    c_cho_phep   : nồng độ CH4 cho phép tại luồng gió ra (%)
    c_gio_vao    : nồng độ CH4 có sẵn trong luồng gió vào (%)
    k_du_phong   : hệ số dự phòng do gió phân bố không đều
    """
    delta = c_cho_phep - c_gio_vao
    if delta <= 0:
        raise ValueError(
            "Nồng độ cho phép phải lớn hơn nồng độ gió vào thì mới pha loãng được."
        )
    q = 100 * q_ch4 / delta * k_du_phong
    kq = KetQua(
        ten="Lưu lượng gió theo khí CH4",
        gia_tri=q,
        don_vi="m3/phút",
        cong_thuc=f"Q = 100 x q_CH4 / (C_cp - C_vào) x k "
                  f"= 100 x {q_ch4} / ({c_cho_phep} - {c_gio_vao}) x {k_du_phong}",
    )
    if delta < 0.2:
        kq.canh_bao.append(
            "Chênh lệch nồng độ quá nhỏ (<0,2%), lưu lượng gió tính ra rất lớn "
            "và nhạy với sai số đo. Nên xem lại số liệu đo khí gió vào."
        )
    return kq


def gio_theo_nguoi(so_nguoi, dinh_muc=4.0, k_du_phong=1.0):
    """Lưu lượng gió theo số người làm việc đồng thời lớn nhất."""
    q = so_nguoi * dinh_muc * k_du_phong
    return KetQua(
        ten="Lưu lượng gió theo số người",
        gia_tri=q,
        don_vi="m3/phút",
        cong_thuc=f"Q = n x q_người x k = {so_nguoi} x {dinh_muc} x {k_du_phong}",
        dien_giai=f"Định mức đang dùng: {dinh_muc} m3/phút cho mỗi người.",
    )


def gio_sau_no_min(khoi_luong_thuoc, tiet_dien, chieu_dai_lo,
                   thoi_gian_thong_gio=30.0, khi_doc_quy_doi=40.0):
    """Lưu lượng gió thông gió lò cụt sau khi nổ mìn (dạng công thức Voronin).

    khoi_luong_thuoc    : lượng thuốc nổ cho một lần nổ (kg)
    tiet_dien           : tiết diện sử dụng của đường lò (m2)
    chieu_dai_lo        : chiều dài đường lò cụt (m)
    thoi_gian_thong_gio : thời gian yêu cầu làm sạch khí (phút)
    khi_doc_quy_doi     : lượng khí độc quy đổi ra CO sinh ra (lít/kg thuốc)

    LƯU Ý: hệ số khí độc quy đổi phụ thuộc loại thuốc nổ đang dùng.
    Đề nghị đối chiếu hộ chiếu nổ mìn và tài liệu thiết kế của Công ty.
    """
    if thoi_gian_thong_gio <= 0:
        raise ValueError("Thời gian thông gió phải lớn hơn 0.")
    duoi_can = (khoi_luong_thuoc * khi_doc_quy_doi
                * tiet_dien ** 2 * chieu_dai_lo ** 2)
    q = (2.25 / thoi_gian_thong_gio) * duoi_can ** (1 / 3)
    kq = KetQua(
        ten="Lưu lượng gió sau nổ mìn",
        gia_tri=q,
        don_vi="m3/phút",
        cong_thuc=f"Q = (2,25 / T) x căn bậc ba của (A x b x S^2 x L^2) "
                  f"= (2,25 / {thoi_gian_thong_gio}) x ∛({khoi_luong_thuoc} x "
                  f"{khi_doc_quy_doi} x {tiet_dien}^2 x {chieu_dai_lo}^2)",
        dien_giai="A = lượng thuốc nổ, b = khí độc quy đổi CO, "
                  "S = tiết diện lò, L = chiều dài lò, T = thời gian thông gió.",
    )
    kq.canh_bao.append(
        "Công thức và hệ số khí độc quy đổi cần đối chiếu với tài liệu thiết kế "
        "thông gió và hộ chiếu nổ mìn đang áp dụng tại Công ty trước khi đưa vào "
        "văn bản chính thức."
    )
    return kq


def toc_do_gio(luu_luong_m3_phut, tiet_dien, v_min=0.25, v_max=4.0):
    """Đổi lưu lượng gió ra tốc độ gió và so với dải cho phép."""
    if tiet_dien <= 0:
        raise ValueError("Tiết diện đường lò phải lớn hơn 0.")
    v = luu_luong_m3_phut / 60.0 / tiet_dien
    kq = KetQua(
        ten="Tốc độ gió trong lò",
        gia_tri=v,
        don_vi="m/s",
        cong_thuc=f"v = Q / (60 x S) = {luu_luong_m3_phut} / (60 x {tiet_dien})",
        dien_giai=f"Dải cho phép đang đặt: {v_min} - {v_max} m/s.",
    )
    if v < v_min or v > v_max:
        kq.vuot_nguong = True
    if v < v_min:
        kq.canh_bao.append(
            f"Tốc độ gió {v:.2f} m/s THẤP HƠN mức tối thiểu {v_min} m/s - "
            "nguy cơ tích tụ khí, cần tăng lưu lượng hoặc giảm tiết diện luồng."
        )
    elif v > v_max:
        kq.canh_bao.append(
            f"Tốc độ gió {v:.2f} m/s VƯỢT mức tối đa {v_max} m/s - "
            "nguy cơ cuốn bụi, cần phân luồng lại hoặc tăng tiết diện."
        )
    return kq


def nong_do_ch4_du_bao(q_ch4, luu_luong_gio, c_gio_vao=0.0, c_cho_phep=1.0):
    """Nồng độ CH4 dự báo tại luồng gió ra ứng với lưu lượng gió thực tế."""
    if luu_luong_gio <= 0:
        raise ValueError("Lưu lượng gió phải lớn hơn 0.")
    c = c_gio_vao + 100 * q_ch4 / luu_luong_gio
    kq = KetQua(
        ten="Nồng độ CH4 dự báo tại luồng gió ra",
        gia_tri=c,
        don_vi="%",
        cong_thuc=f"C = C_vào + 100 x q_CH4 / Q "
                  f"= {c_gio_vao} + 100 x {q_ch4} / {luu_luong_gio}",
        dien_giai=f"Ngưỡng cho phép đang đặt: {c_cho_phep} %.",
    )
    if c >= c_cho_phep:
        kq.vuot_nguong = True
        kq.canh_bao.append(
            f"Nồng độ dự báo {c:.3f}% ĐẠT/VƯỢT ngưỡng {c_cho_phep}% - "
            "phải tăng lưu lượng gió hoặc xử lý nguồn phát khí trước khi sản xuất."
        )
    elif c >= 0.8 * c_cho_phep:
        kq.canh_bao.append(
            f"Nồng độ dự báo {c:.3f}% đã đạt trên 80% ngưỡng - cần theo dõi sát."
        )
    return kq


# --------------------------------------------------------------- THOÁT NƯỚC

def luu_luong_nuoc_mua(dien_tich_ha, luong_mua_mm, he_so_dong_chay=0.6,
                       thoi_gian_gio=24.0):
    """Lưu lượng nước mưa chảy về mỏ ước tính.

    dien_tich_ha    : diện tích lưu vực hứng nước (ha)
    luong_mua_mm    : lượng mưa trong đợt (mm)
    he_so_dong_chay : hệ số dòng chảy/thấm về mỏ (0 - 1)
    thoi_gian_gio   : thời gian đợt mưa quy đổi (giờ)
    """
    if thoi_gian_gio <= 0:
        raise ValueError("Thời gian phải lớn hơn 0.")
    the_tich = dien_tich_ha * 10000 * (luong_mua_mm / 1000.0) * he_so_dong_chay
    q = the_tich / thoi_gian_gio
    return KetQua(
        ten="Lưu lượng nước mưa về mỏ (trung bình)",
        gia_tri=q,
        don_vi="m3/giờ",
        cong_thuc=f"V = F x h x alpha = {dien_tich_ha} ha x {luong_mua_mm} mm x "
                  f"{he_so_dong_chay} = {the_tich:,.0f} m3 ; Q = V / T = "
                  f"{the_tich:,.0f} / {thoi_gian_gio}",
        dien_giai=f"Tổng lượng nước cả đợt ước tính {the_tich:,.0f} m3.",
    )


def nang_luc_bom(q_nuoc_ve, q_mot_bom, so_bom_hoat_dong, he_so_du_phong=1.2):
    """Kiểm tra năng lực trạm bơm so với lượng nước chảy về."""
    nang_luc = q_mot_bom * so_bom_hoat_dong
    yeu_cau = q_nuoc_ve * he_so_du_phong
    kq = KetQua(
        ten="Năng lực bơm hiện có",
        gia_tri=nang_luc,
        don_vi="m3/giờ",
        cong_thuc=f"Q_bơm = q1 x n = {q_mot_bom} x {so_bom_hoat_dong} ; "
                  f"Yêu cầu = Q_về x k = {q_nuoc_ve} x {he_so_du_phong} "
                  f"= {yeu_cau:,.1f} m3/giờ",
        dien_giai=f"Nước chảy về {q_nuoc_ve:,.1f} m3/giờ, "
                  f"yêu cầu tối thiểu {yeu_cau:,.1f} m3/giờ (đã tính dự phòng).",
    )
    if nang_luc < yeu_cau:
        kq.vuot_nguong = True
        thieu = yeu_cau - nang_luc
        can_them = thieu / q_mot_bom if q_mot_bom > 0 else 0
        kq.canh_bao.append(
            f"THIẾU {thieu:,.1f} m3/giờ - tương đương cần bổ sung khoảng "
            f"{can_them:.1f} bơm cùng loại hoặc nâng công suất."
        )
    return kq


def thoi_gian_thao_kho(the_tich_nuoc, q_bom, q_nuoc_ve=0.0):
    """Thời gian tháo khô một khu vực ngập."""
    hieu_dung = q_bom - q_nuoc_ve
    if hieu_dung <= 0:
        raise ValueError(
            "Năng lực bơm không lớn hơn lượng nước chảy về - không thể tháo khô. "
            "Phải bổ sung bơm hoặc chặn nguồn nước trước."
        )
    t = the_tich_nuoc / hieu_dung
    return KetQua(
        ten="Thời gian tháo khô",
        gia_tri=t,
        don_vi="giờ",
        cong_thuc=f"T = V / (Q_bơm - Q_về) = {the_tich_nuoc} / "
                  f"({q_bom} - {q_nuoc_ve})",
        dien_giai=f"Tương đương khoảng {t/24:.1f} ngày bơm liên tục. "
                  f"Lưu lượng bơm hiệu dụng {hieu_dung:,.1f} m3/giờ.",
    )


def dung_tich_du_tru_ham_bom(q_nuoc_ve, gio_du_tru=4.0):
    """Dung tích hầm chứa nước tối thiểu để cầm cự khi mất điện/hỏng bơm."""
    v = q_nuoc_ve * gio_du_tru
    return KetQua(
        ten="Dung tích hầm chứa tối thiểu",
        gia_tri=v,
        don_vi="m3",
        cong_thuc=f"V = Q_về x T_dự trữ = {q_nuoc_ve} x {gio_du_tru}",
        dien_giai=f"Đủ chứa nước chảy về trong {gio_du_tru} giờ khi bơm dừng.",
    )
