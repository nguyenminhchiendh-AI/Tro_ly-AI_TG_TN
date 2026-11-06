# Kết quả chạy giả lập — Trợ lý Thông gió & Thoát nước

**Ngày chạy:** 27/10/2026
**Mục đích:** kiểm chứng toàn bộ 9 phép tính của ứng dụng trước khi đưa vào sử dụng.

> ⚠️ **TOÀN BỘ SỐ LIỆU DƯỚI ĐÂY LÀ GIẢ ĐỊNH** để kiểm thử công cụ.
> Không phải số liệu thực tế của Công ty than Dương Huy.
> Các ngưỡng dùng trong bài chạy cũng là ngưỡng tham khảo, chưa thẩm định.

---

## Kịch bản A — Thông gió lò chợ 7-1 mức -100

**Giả định đầu vào:** lưu lượng CH4 thoát ra 3,2 m³/phút; nồng độ CH4 gió vào
0,15%; ngưỡng cho phép 1,0%; 42 người/ca; tiết diện lò 7,2 m².

| # | Nội dung | Kết quả | Trạng thái |
|---|---|---|---|
| A1 | Lưu lượng gió cần theo khí CH4 (k=1,4) | **527,06 m³/phút** | ✅ Đạt |
| A2 | Lưu lượng gió theo số người (42 × 4) | **168,00 m³/phút** | ✅ Đạt |
| A3 | Tốc độ gió với Q=527, S=7,2 m² | **1,22 m/s** | ✅ Đạt (dải 0,25–4,0) |
| A4 | Tốc độ gió khi tiết diện tụt còn 2,4 m² | **3,66 m/s** | ✅ Đạt, sát trần |
| A5 | CH4 dự báo khi quạt tụt còn 300 m³/phút | **1,22 %** | 🚫 **KHÔNG ĐẠT** |
| A6 | CH4 dự báo với Q thiết kế 527 m³/phút | **0,76 %** | ✅ Đạt |
| A7 | Gió thông lò cụt sau nổ mìn (28 kg, L=180 m) | **112,16 m³/phút** | ⚠️ Cần đối chiếu |
| A8 | *Nhập sai:* ngưỡng 0,10% < gió vào 0,15% | — | 🛑 App chặn lại |

**Kết luận A:** lưu lượng gió chi phối là **527 m³/phút theo khí CH4**, lớn gấp
hơn 3 lần yêu cầu theo số người (168 m³/phút). Nếu quạt tụt xuống 300 m³/phút
thì nồng độ CH4 vượt ngưỡng ngay — đây là biên an toàn cần giám sát chặt.

---

## Kịch bản B — Thoát nước mùa mưa bão, lưu vực mức -100

**Giả định đầu vào:** lưu vực hứng nước 15 ha; lượng mưa đợt 250 mm;
hệ số dòng chảy về mỏ 0,65; đợt mưa 24 giờ; trạm bơm 200 m³/giờ mỗi bơm.

| # | Nội dung | Kết quả | Trạng thái |
|---|---|---|---|
| B1 | Nước mưa về mỏ (tổng đợt 24.375 m³) | **1.015,62 m³/giờ** | ✅ Đạt |
| B2 | Năng lực 4 bơm × 200 m³/giờ | **800 m³/giờ** | 🚫 **KHÔNG ĐẠT — thiếu 418,7** |
| B3 | Sau khi bổ sung thành 7 bơm | **1.400 m³/giờ** | ✅ Đạt |
| B4 | Tháo khô 12.000 m³ bằng 4 bơm, nước vẫn về | — | 🛑 App chặn lại |
| B5 | Tháo khô 12.000 m³ bằng 7 bơm, nước về còn 300 | **10,91 giờ** | ✅ Đạt |
| B6 | Dung tích hầm chứa cầm cự 4 giờ mất điện | **4.062,40 m³** | ✅ Đạt |

**Kết luận B:** với đợt mưa 250 mm, **4 bơm là không đủ** — thiếu khoảng
418,7 m³/giờ, tương đương cần bổ sung khoảng 2,1 bơm cùng loại.
Ở trường hợp B4 app **từ chối tính và giải thích lý do** thay vì đưa ra một con
số vô nghĩa: năng lực bơm 800 m³/giờ nhỏ hơn lượng nước về 1.015,6 m³/giờ thì
mực nước chỉ dâng lên, không thể tháo khô.

---

## Hai điểm đáng chú ý rút ra từ lần chạy này

### 1. App biết từ chối khi đề bài vô lý
Trường hợp A8 và B4 không cho ra số. App dừng lại và nói rõ lý do.
Đây là điểm khác biệt quan trọng so với để AI tính nhẩm — AI thường vẫn
"nặn" ra một con số nghe hợp lý trong những tình huống như vậy.

### 2. Đã sửa một lỗi thiết kế phát hiện trong lúc chạy
Ban đầu ô kết quả **luôn tô xanh** kể cả khi vượt ngưỡng, cảnh báo chỉ nằm ở
dòng chữ phía dưới — liếc nhanh rất dễ bỏ sót. Đã sửa thành 3 màu:

| Màu | Ý nghĩa |
|---|---|
| 🔴 Đỏ — "KHÔNG ĐẠT" | Đã phá vỡ ngưỡng an toàn |
| 🟡 Vàng — "CẦN LƯU Ý" | Có cảnh báo cần đọc kỹ |
| 🟢 Xanh | Không có vấn đề |

---

## Phần chưa giả lập được

**Tab Hỏi đáp chuyên môn chưa chạy thử được** vì phiên làm việc này không có
khoá OpenAI API. Tôi chỉ kiểm chứng được phần khung: app gọi API đúng cách,
và khi khoá sai/thiếu thì báo lỗi êm chứ không sập.
Chất lượng câu trả lời của trợ lý thì anh phải tự thử sau khi triển khai.
