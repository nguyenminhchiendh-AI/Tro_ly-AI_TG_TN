# Công cụ CAD — Mặt cắt A-A lò chợ (Phòng KCM, Công ty than Dương Huy)

Bộ script đọc/ghi file **DXF** của AutoCAD, dùng để rút ngắn thời gian vẽ
bản vẽ biện pháp đào – chống lò.

> ⚠️ Các script này **không đọc được file `.dwg`**. Trong AutoCAD bấm
> `File → Save As → AutoCAD 2013 DXF (*.dxf)` trước khi dùng, và khi xong
> thì mở file kết quả rồi `Save As` ngược lại thành `.dwg`.

---

## 1. `keodai_lo_cho.py` — kéo dài / rút ngắn mặt cắt A-A

**Đây là công cụ chính.** Nó **không vẽ lại gì cả**: lấy chính bản vẽ gốc của
Công ty, cắt tại một vị trí giữa đoạn lặp, đẩy toàn bộ phần phía trên ra xa,
rồi nhân bản đúng số bộ vì chống cần thêm vào chỗ trống. Mọi nét vẽ, ký hiệu,
ghi chú giữ nguyên 100%.

```
python cad/keodai_lo_cho.py  <ban_ve_goc.dxf>  <ban_ve_moi.dxf>  <so_vi_them>  ["L=46m"]
```

| Tham số | Ý nghĩa |
|---|---|
| `so_vi_them` | Số bộ vì chống thêm vào. Mỗi bộ = 1 bước 1000 mm. Số âm = rút ngắn |
| `"L=46m"` | Tuỳ chọn — chữ ghi trên đường kích thước tổng chiều dài |

Ví dụ — kéo dài thêm 6 bộ vì (6 m) và đổi nhãn thành `L=46m`:

```
python cad/keodai_lo_cho.py matcat-A-A.dxf matcat-A-A_46m.dxf 6 "L=46m"
```

### Thông số khung toạ độ (sửa trong đầu file khi dùng cho bản vẽ khác)

Các giá trị này đo được từ bản vẽ `matcat-A-A_TT-9-8`:

| Hằng số | Giá trị | Ý nghĩa |
|---|---|---|
| `GOC_DOC` | `-28.0` | Hướng trục lò chợ, độ |
| `O` | `(1771875, -491085)` | Gốc toạ độ, nằm trên đường nền lò |
| `BUOC` | `1000` | Bước lặp của vì chống, mm |
| `U_CAT` | `20698` | Vị trí cắt, phải nằm giữa đoạn lặp |

---

## 2. `thu_vien_block.py` — bày thư viện ký hiệu

Trích toàn bộ ký hiệu (block) đang dùng trong bản vẽ, bày thành bảng mẫu có
khung và nhãn, đổi tên 4 ký hiệu chính sang tên đọc được:

| Tên mới | Tên gốc trong bản vẽ | Dùng |
|---|---|---|
| `LC_XA-SVP+DAU-COT-TLD` | `83fsdfsdffawer23r23r23r` | 19 lần |
| `LC_COT-TLD-DZ` | `83DFGDFGRTERT` | 25 lần |
| `LC_DE-COT` | `83GDFG4TERTWE` | 25 lần |
| `LC_KYHIEU-TRON-3NHANH` | `83A$C1038421F` | 14 lần |

```
python cad/thu_vien_block.py <ban_ve_goc.dxf> <thu_vien.dxf>
```

---

## 3. `sinh_matcat_AA.py` — dựng mới mặt cắt A-A từ tham số

Dựng bản vẽ từ đầu theo các số nhập ở đầu file (số vì, bước cột, góc dốc,
chiều cao lò, chiều dày vỉa, tên lò…), dùng lại block thật của Công ty.

```
python cad/sinh_matcat_AA.py <ban_ve_goc.dxf> <ban_ve_moi.dxf>
```

> ⚠️ Script này **chưa tái tạo chính xác** phần cột chống vẽ bằng nét
> (`ve_cot`) — số liệu là em đo từ bản vẽ gốc, cần đối chiếu lại.
> Khi chỉ cần đổi chiều dài lò chợ thì **dùng `keodai_lo_cho.py` sẽ chuẩn hơn.**

---

## Số liệu đo được từ bản vẽ `matcat-A-A_TT-9-8_thu1.dxf`

| Hạng mục | Giá trị |
|---|---|
| Lò chợ | TT-9-8(TT)/V9-KTT, giữa lò DVVT chợ (dưới) và lò BXTG chợ (trên) |
| Tỷ lệ | 1/100 |
| Góc dốc vỉa | 28° |
| Chiều dài lò chợ | ghi nhãn `L=40m` (đoạn vẽ trên hình ≈ 24 m — vẽ rút gọn) |
| Chiều cao lò chợ | 2 228 mm (nền → nóc) |
| Chiều dày vỉa | 3 420 mm, ghi nhãn `2500 ÷ 3500` |
| Vì chống | Xà thép SVP + cột TLĐ DZ(22÷28), tiến trước 10 m |
| Bước vì chống | 1 000 mm (19 bộ vẽ trên hình) |
| Khoảng cách cột | 500 mm (chuỗi kích thước 500-500) |
| Cược chắn than | sole 6 m/cược |
| Chống tăng cường | Cột TLĐ DW-25 chống xà tăng cường |
| Thiết bị | Máng cào, máng trượt, bậc lên xuống |

## Việc cần kiểm tra

- [ ] Mở file kết quả bằng AutoCAD thật để xác nhận (môi trường sinh file
      không có AutoCAD, mới chỉ kiểm tra bằng thư viện đồ hoạ)
- [ ] Đường nền kẻ đậm trên layer `GO` (đoạn u = 3 370 → 18 257) kết thúc
      giữa chừng trong bản vẽ gốc nên không tự dài ra — kéo tay 1 nét sau khi chạy
- [ ] Đối chiếu tên block mới đặt với quy ước đặt tên của Phòng
