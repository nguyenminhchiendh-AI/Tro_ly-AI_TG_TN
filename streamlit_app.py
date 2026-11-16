# -*- coding: utf-8 -*-
"""
Trợ lý Thông gió - Khí mỏ - Thoát nước
Phòng Kỹ thuật công nghệ mỏ (KCM) - Công ty than Dương Huy - TKV
"""

import os
import re
from datetime import datetime

import streamlit as st
from openai import OpenAI

import tinhtoan as tt

st.set_page_config(page_title="Trợ lý KCM - Thông gió & Thoát nước",
                   page_icon="⛏️", layout="wide")

THU_MUC = os.path.dirname(os.path.abspath(__file__))


def rfile(ten_file, mac_dinh=""):
    """Đọc file văn bản trong thư mục ứng dụng, không làm sập app nếu thiếu."""
    duong_dan = os.path.join(THU_MUC, ten_file)
    try:
        with open(duong_dan, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return mac_dinh


def doc_mau_nhac():
    """Đọc thư viện mẫu nhắc, trả về list (nhom, ten_nut, noi_dung).

    Chỉ đọc phần nằm sau dòng kẻ ngang "---" để không bắt nhầm dòng ví dụ
    trong phần hướng dẫn ở đầu file.
    """
    noi_dung = rfile("kienthuc/mau_nhac.md")
    if "\n---" in noi_dung:
        noi_dung = noi_dung.split("\n---", 1)[1]
    mau = []
    for dong in noi_dung.splitlines():
        khop = re.match(r"^-\s*\[(.+?)\]\s*(.+?)\s*::\s*(.+)$", dong.strip())
        if khop:
            mau.append((khop.group(1), khop.group(2), khop.group(3)))
    return mau


def lay_api_key():
    """Ưu tiên st.secrets, sau đó đến biến môi trường."""
    try:
        khoa = st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        khoa = ""
    return khoa or os.environ.get("OPENAI_API_KEY", "")


MO_HINH = (rfile("module_chatgpt.txt", "gpt-4o-mini").strip()
           or "gpt-4o-mini")
SYSTEM_PROMPT = rfile("01.system_trainning.txt")
LOI_MO_DAU = rfile("02.assistant.txt")
TIEU_DE = rfile("00.xinchao.txt", "Trợ lý KCM").strip()

# Giới hạn số lượt hội thoại gửi lên API để kiểm soát chi phí
SO_LUOT_GIU = 20


def khoi_tao_hoi_thoai():
    st.session_state.messages = [{"role": "assistant", "content": LOI_MO_DAU}]


if "messages" not in st.session_state:
    khoi_tao_hoi_thoai()
if "nhac_cho" not in st.session_state:
    st.session_state.nhac_cho = None


# ------------------------------------------------------------------ GIAO DIỆN

cot_logo, cot_tieu_de = st.columns([1, 6])
with cot_logo:
    if os.path.exists(os.path.join(THU_MUC, "logo.png")):
        st.image(os.path.join(THU_MUC, "logo.png"), use_container_width=True)
with cot_tieu_de:
    st.markdown(f"### {TIEU_DE}")
    st.caption("Công ty than Dương Huy - TKV | Công cụ hỗ trợ nội bộ, "
               "không thay thế văn bản quy phạm")

tab_chat, tab_gio, tab_nuoc, tab_tra = st.tabs(
    ["💬 Hỏi đáp chuyên môn", "🌬️ Máy tính thông gió",
     "💧 Máy tính thoát nước", "📋 Tra cứu ngưỡng"]
)


# ------------------------------------------------------------ TAB: HỎI ĐÁP

with st.sidebar:
    st.subheader("⚡ Mẫu nhắc nhanh")
    st.caption("Bấm để đưa sẵn câu hỏi vào ô chat")
    danh_sach = doc_mau_nhac()
    nhom_hien_co = sorted({n for n, _, _ in danh_sach})
    for nhom in nhom_hien_co:
        with st.expander(nhom, expanded=False):
            for i, (n, ten, noi_dung) in enumerate(danh_sach):
                if n != nhom:
                    continue
                if st.button(ten, key=f"mau_{nhom}_{i}", use_container_width=True):
                    st.session_state.nhac_cho = noi_dung
                    st.rerun()

    st.divider()
    st.subheader("🛠️ Hội thoại")
    if st.button("🗑️ Xoá & bắt đầu lại", use_container_width=True):
        khoi_tao_hoi_thoai()
        st.rerun()

    ban_ghi = "\n\n".join(
        f"### {'TRỢ LÝ' if m['role'] == 'assistant' else 'SẾP'}\n{m['content']}"
        for m in st.session_state.messages
    )
    st.download_button(
        "📥 Tải hội thoại (.md)",
        data=f"# Trao đổi với Trợ lý KCM\n"
             f"_Ngày {datetime.now():%d/%m/%Y %H:%M}_\n\n{ban_ghi}",
        file_name=f"trao_doi_KCM_{datetime.now():%Y%m%d_%H%M}.md",
        mime="text/markdown",
        use_container_width=True,
    )
    st.caption(f"Mô hình: `{MO_HINH}`")


def gui_cau_hoi(cau_hoi: str):
    """Gửi câu hỏi lên API và hiển thị phản hồi theo kiểu chảy chữ."""
    st.session_state.messages.append({"role": "user", "content": cau_hoi})
    with st.chat_message("user"):
        st.markdown(cau_hoi)

    api_key = lay_api_key()
    if not api_key:
        loi = ("⚠️ **Chưa có khoá OPENAI_API_KEY.** Sếp vào phần Settings → "
               "Secrets của ứng dụng (hoặc đặt biến môi trường "
               "`OPENAI_API_KEY`) để nhập khoá rồi tải lại trang.")
        with st.chat_message("assistant"):
            st.warning(loi)
        st.session_state.messages.append({"role": "assistant", "content": loi})
        return

    lich_su = st.session_state.messages[-SO_LUOT_GIU:]
    gui_di = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m["role"], "content": m["content"]} for m in lich_su
    ]

    with st.chat_message("assistant"):
        try:
            luong = OpenAI(api_key=api_key).chat.completions.create(
                model=MO_HINH, messages=gui_di, stream=True,
            )
            phan_hoi = st.write_stream(
                chunk.choices[0].delta.content or ""
                for chunk in luong if chunk.choices
            )
        except Exception as loi_api:
            phan_hoi = (f"⚠️ **Không gọi được API.** Chi tiết: `{loi_api}`\n\n"
                        "Sếp kiểm tra lại khoá API, kết nối mạng, "
                        "hoặc hạn mức sử dụng của tài khoản.")
            st.error(phan_hoi)

    st.session_state.messages.append({"role": "assistant", "content": phan_hoi})


with tab_chat:
    for tin in st.session_state.messages:
        if tin["role"] in ("user", "assistant"):
            with st.chat_message(tin["role"]):
                st.markdown(tin["content"])

    cho_gui = st.session_state.nhac_cho
    st.session_state.nhac_cho = None
    nhap_vao = st.chat_input("Sếp nhập nội dung cần trao đổi...")
    cau_hoi = cho_gui or nhap_vao
    if cau_hoi:
        gui_cau_hoi(cau_hoi)
        st.rerun()


# --------------------------------------------------------- HIỂN THỊ KẾT QUẢ

def hien_ket_qua(kq: tt.KetQua, khoa: str):
    # Mau o ket qua phai phan anh dung trang thai an toan:
    # do = pha vo nguong, vang = co luu y can doc, xanh = khong co van de.
    nhan = f"**{kq.ten}: {kq.gia_tri:,.2f} {kq.don_vi}**"
    if kq.vuot_nguong:
        st.error("🚫 KHÔNG ĐẠT — " + nhan)
    elif kq.canh_bao:
        st.warning("⚠️ CẦN LƯU Ý — " + nhan)
    else:
        st.success("✅ " + nhan)
    st.caption(f"Công thức đã dùng: {kq.cong_thuc}")
    if kq.dien_giai:
        st.info(kq.dien_giai)
    for c in kq.canh_bao:
        st.warning(c)
    if st.button("🤖 Gửi kết quả sang tab Hỏi đáp để phân tích", key=f"hoi_{khoa}"):
        st.session_state.nhac_cho = (
            "Em phân tích giúp anh kết quả tính toán sau, nêu rõ kết quả này "
            "có đạt yêu cầu không, rủi ro gì cần lưu ý và biện pháp xử lý "
            "cụ thể tại mỏ hầm lò:\n\n```\n" + kq.tom_tat() + "\n```"
        )
        st.rerun()


def chay(ham, khoa, **tham_so):
    try:
        hien_ket_qua(ham(**tham_so), khoa)
    except ValueError as loi:
        st.error(f"⚠️ {loi}")


# ------------------------------------------------------ TAB: MÁY TÍNH GIÓ

with tab_gio:
    st.caption("Phép tính do máy thực hiện, không phải AI ước lượng. "
               "Các ngưỡng cho phép là ô nhập được — sếp sửa theo văn bản "
               "đang áp dụng tại Công ty.")

    with st.expander("1️⃣ Lưu lượng gió cần thiết theo khí CH4", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        q_ch4 = c1.number_input("Lưu lượng CH4 thoát ra (m³/phút)",
                                0.0, 500.0, 2.0, 0.1, key="g1a")
        c_cp = c2.number_input("Nồng độ CH4 cho phép (%)",
                               0.01, 10.0, 1.0, 0.05, key="g1b")
        c_vao = c3.number_input("CH4 trong gió vào (%)",
                                0.0, 5.0, 0.0, 0.05, key="g1c")
        k_dp = c4.number_input("Hệ số dự phòng",
                               1.0, 3.0, 1.4, 0.1, key="g1d")
        if st.button("Tính", key="btn_g1"):
            chay(tt.gio_theo_ch4, "g1", q_ch4=q_ch4, c_cho_phep=c_cp,
                 c_gio_vao=c_vao, k_du_phong=k_dp)

    with st.expander("2️⃣ Lưu lượng gió theo số người làm việc"):
        c1, c2, c3 = st.columns(3)
        n_ng = c1.number_input("Số người đồng thời lớn nhất",
                               1, 2000, 25, 1, key="g2a")
        dm = c2.number_input("Định mức (m³/phút/người)",
                             1.0, 20.0, 4.0, 0.5, key="g2b")
        k2 = c3.number_input("Hệ số dự phòng", 1.0, 3.0, 1.0, 0.1, key="g2c")
        if st.button("Tính", key="btn_g2"):
            chay(tt.gio_theo_nguoi, "g2", so_nguoi=n_ng,
                 dinh_muc=dm, k_du_phong=k2)

    with st.expander("3️⃣ Tốc độ gió trong lò và kiểm tra ngưỡng"):
        c1, c2, c3, c4 = st.columns(4)
        q3 = c1.number_input("Lưu lượng gió (m³/phút)",
                             0.0, 50000.0, 600.0, 10.0, key="g3a")
        s3 = c2.number_input("Tiết diện sử dụng (m²)",
                             0.1, 100.0, 8.5, 0.1, key="g3b")
        vmin = c3.number_input("Tốc độ tối thiểu (m/s)",
                               0.0, 5.0, 0.25, 0.05, key="g3c")
        vmax = c4.number_input("Tốc độ tối đa (m/s)",
                               0.5, 20.0, 4.0, 0.5, key="g3d")
        if st.button("Tính", key="btn_g3"):
            chay(tt.toc_do_gio, "g3", luu_luong_m3_phut=q3,
                 tiet_dien=s3, v_min=vmin, v_max=vmax)

    with st.expander("4️⃣ Nồng độ CH4 dự báo với lưu lượng gió thực tế"):
        c1, c2, c3, c4 = st.columns(4)
        q4 = c1.number_input("Lưu lượng CH4 thoát ra (m³/phút)",
                             0.0, 500.0, 2.0, 0.1, key="g4a")
        qg4 = c2.number_input("Lưu lượng gió thực tế (m³/phút)",
                              1.0, 50000.0, 400.0, 10.0, key="g4b")
        cv4 = c3.number_input("CH4 trong gió vào (%)",
                              0.0, 5.0, 0.0, 0.05, key="g4c")
        cp4 = c4.number_input("Ngưỡng cho phép (%)",
                              0.01, 10.0, 1.0, 0.05, key="g4d")
        if st.button("Tính", key="btn_g4"):
            chay(tt.nong_do_ch4_du_bao, "g4", q_ch4=q4, luu_luong_gio=qg4,
                 c_gio_vao=cv4, c_cho_phep=cp4)

    with st.expander("5️⃣ Lưu lượng gió thông lò cụt sau nổ mìn"):
        st.warning("Công thức và hệ số khí độc quy đổi cần đối chiếu với "
                   "tài liệu thiết kế và hộ chiếu nổ mìn của Công ty.")
        c1, c2, c3, c4, c5 = st.columns(5)
        a5 = c1.number_input("Thuốc nổ (kg)", 0.1, 500.0, 30.0, 1.0, key="g5a")
        s5 = c2.number_input("Tiết diện lò (m²)", 0.5, 100.0, 9.6, 0.1, key="g5b")
        l5 = c3.number_input("Chiều dài lò (m)", 1.0, 3000.0, 250.0, 10.0, key="g5c")
        t5 = c4.number_input("Thời gian thông gió (phút)",
                             1.0, 240.0, 30.0, 5.0, key="g5d")
        b5 = c5.number_input("Khí độc quy đổi CO (l/kg)",
                             1.0, 200.0, 40.0, 1.0, key="g5e")
        if st.button("Tính", key="btn_g5"):
            chay(tt.gio_sau_no_min, "g5", khoi_luong_thuoc=a5, tiet_dien=s5,
                 chieu_dai_lo=l5, thoi_gian_thong_gio=t5, khi_doc_quy_doi=b5)


# ---------------------------------------------------- TAB: MÁY TÍNH NƯỚC

with tab_nuoc:
    st.caption("Phục vụ công tác thoát nước mỏ và phòng chống ngập mỏ.")

    with st.expander("1️⃣ Ước tính lượng nước mưa về mỏ", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        f1 = c1.number_input("Diện tích lưu vực (ha)",
                             0.1, 5000.0, 12.0, 0.5, key="n1a")
        h1 = c2.number_input("Lượng mưa đợt (mm)",
                             1.0, 2000.0, 180.0, 10.0, key="n1b")
        a1 = c3.number_input("Hệ số dòng chảy về mỏ",
                             0.01, 1.0, 0.6, 0.05, key="n1c")
        t1 = c4.number_input("Thời gian đợt mưa (giờ)",
                             1.0, 240.0, 24.0, 1.0, key="n1d")
        if st.button("Tính", key="btn_n1"):
            chay(tt.luu_luong_nuoc_mua, "n1", dien_tich_ha=f1,
                 luong_mua_mm=h1, he_so_dong_chay=a1, thoi_gian_gio=t1)

    with st.expander("2️⃣ Kiểm tra năng lực trạm bơm"):
        c1, c2, c3, c4 = st.columns(4)
        qv2 = c1.number_input("Nước chảy về (m³/giờ)",
                              0.0, 20000.0, 500.0, 10.0, key="n2a")
        q12 = c2.number_input("Lưu lượng 1 bơm (m³/giờ)",
                              1.0, 5000.0, 180.0, 10.0, key="n2b")
        sb2 = c3.number_input("Số bơm hoạt động", 1, 50, 3, 1, key="n2c")
        kd2 = c4.number_input("Hệ số dự phòng",
                              1.0, 3.0, 1.2, 0.1, key="n2d")
        if st.button("Tính", key="btn_n2"):
            chay(tt.nang_luc_bom, "n2", q_nuoc_ve=qv2, q_mot_bom=q12,
                 so_bom_hoat_dong=sb2, he_so_du_phong=kd2)

    with st.expander("3️⃣ Thời gian tháo khô khu vực ngập"):
        c1, c2, c3 = st.columns(3)
        v3 = c1.number_input("Thể tích nước ngập (m³)",
                             1.0, 500000.0, 8000.0, 100.0, key="n3a")
        qb3 = c2.number_input("Năng lực bơm (m³/giờ)",
                              1.0, 20000.0, 540.0, 10.0, key="n3b")
        qv3 = c3.number_input("Nước tiếp tục chảy về (m³/giờ)",
                              0.0, 20000.0, 300.0, 10.0, key="n3c")
        if st.button("Tính", key="btn_n3"):
            chay(tt.thoi_gian_thao_kho, "n3", the_tich_nuoc=v3,
                 q_bom=qb3, q_nuoc_ve=qv3)

    with st.expander("4️⃣ Dung tích hầm chứa nước tối thiểu"):
        c1, c2 = st.columns(2)
        qv4 = c1.number_input("Nước chảy về (m³/giờ)",
                              0.0, 20000.0, 500.0, 10.0, key="n4a")
        gd4 = c2.number_input("Số giờ dự trữ khi sự cố",
                              0.5, 48.0, 4.0, 0.5, key="n4b")
        if st.button("Tính", key="btn_n4"):
            chay(tt.dung_tich_du_tru_ham_bom, "n4",
                 q_nuoc_ve=qv4, gio_du_tru=gd4)


# --------------------------------------------------------- TAB: TRA CỨU

with tab_tra:
    st.error("**Bảng dưới đây CHƯA ĐƯỢC THẨM ĐỊNH.** Đây là bản nháp để sếp "
             "hiệu chỉnh. Mọi trị số phải đối chiếu QCVN 01:2011/BCT bản hiện "
             "hành và quy định nội bộ Công ty trước khi dùng trong văn bản "
             "chính thức. Sếp sửa file `kienthuc/nguong_an_toan.md` trên "
             "GitHub là nội dung ở đây cập nhật theo.")
    st.markdown(rfile("kienthuc/nguong_an_toan.md",
                      "_Chưa có file kienthuc/nguong_an_toan.md_"))
