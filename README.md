# ⛏️ Trợ lý Thông gió – Khí mỏ – Thoát nước

Công cụ hỗ trợ nội bộ Phòng Kỹ thuật công nghệ mỏ (KCM) — Công ty than Dương Huy - TKV.

> ⚠️ **Đây là công cụ hỗ trợ, KHÔNG thay thế văn bản quy phạm.**
> Mọi trị số, công thức trong ứng dụng phải được đối chiếu với QCVN 01:2011/BCT
> (bản hiện hành) và quy định nội bộ của Công ty trước khi đưa vào thiết kế,
> báo cáo hoặc quyết định.

## Ứng dụng có gì

| Tab | Công dụng |
|---|---|
| 💬 **Hỏi đáp chuyên môn** | Trợ lý AI đã được nạp kiến thức ngành: thông gió, khí mỏ, thoát nước, than tự cháy, khoan thăm dò, ƯCSC, quản lý phân xưởng |
| 🌬️ **Máy tính thông gió** | Lưu lượng gió theo CH4 / theo số người / sau nổ mìn, tốc độ gió, nồng độ CH4 dự báo |
| 💧 **Máy tính thoát nước** | Nước mưa về mỏ, năng lực trạm bơm, thời gian tháo khô, dung tích hầm chứa |
| 📋 **Tra cứu ngưỡng** | Bảng ngưỡng an toàn để tra nhanh |

**Điểm quan trọng:** mọi phép tính do Python thực hiện, **không phải AI tính nhẩm**.
Mỗi kết quả đều hiện rõ công thức đã dùng để người kiểm tra đối chiếu được,
và tự cảnh báo khi vượt ngưỡng. Bấm nút *"Đưa kết quả này sang trợ lý phân tích"*
để chuyển số liệu vừa tính sang tab hỏi đáp.

## Cách sửa nội dung (không cần biết lập trình)

Sửa trực tiếp trên GitHub: mở file → bấm biểu tượng **cây bút ✏️** → sửa → *Commit changes*.

| Muốn đổi | Sửa file |
|---|---|
| Cách trợ lý trả lời, kiến thức nền | `01.system_trainning.txt` |
| Lời chào mở đầu | `02.assistant.txt` |
| Tiêu đề ứng dụng | `00.xinchao.txt` |
| Các nút "Mẫu nhắc nhanh" | `kienthuc/mau_nhac.md` |
| Bảng ngưỡng an toàn | `kienthuc/nguong_an_toan.md` |
| Mô hình AI sử dụng | `module_chatgpt.txt` |

### Thêm một nút mẫu nhắc nhanh
Mở `kienthuc/mau_nhac.md`, thêm một dòng **sau dấu `---`** theo đúng mẫu:

```
- [Thông gió] Tên nút ngắn :: Nội dung câu hỏi đầy đủ gửi cho trợ lý.
```

## Việc cần làm trước khi dùng chính thức

- [ ] Rà soát và xác nhận từng trị số trong `kienthuc/nguong_an_toan.md`
      theo QCVN 01:2011/BCT bản hiện hành
- [ ] Đối chiếu công thức tính gió sau nổ mìn với hộ chiếu nổ mìn của Công ty
- [ ] Xác định hệ số dòng chảy nước mưa về mỏ theo số liệu thực tế từng khu vực

## Cài đặt khoá API

Khoá API **không được đưa lên GitHub** (đã chặn bằng `.gitignore`).

- Chạy trên Streamlit Community Cloud: khai báo tại **Settings → Secrets**
- Chạy trên máy: copy `.streamlit/secrets.toml.example` thành `.streamlit/secrets.toml`
  rồi dán khoá thật vào
- Hoặc đặt biến môi trường `OPENAI_API_KEY`

> 🔎 **Lưu ý đã kiểm chứng:** nếu trong thư mục có file `.streamlit/secrets.toml`
> chứa dòng `OPENAI_API_KEY = ""` (để trống), Streamlit sẽ **ghi đè lên biến
> môi trường bằng giá trị rỗng** và ứng dụng báo "chưa có khoá" dù khoá thật đã
> được đặt. Vì vậy file rỗng này đã được gỡ khỏi kho. Chỉ tạo `secrets.toml`
> khi thực sự dán khoá thật vào.

## Chạy trên máy

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
