# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Đạt (cả 3 floor) | **dùng** — chỉ cho chất lượng giọng văn, non-blocking; không dùng cho tiền/approval |
| helpful | 100 | 0.375 | 1.000 | 0.300 | **Không đạt** (κ < 0.6, R < 0.7) | **loại** — không được dùng làm gate |

Ma trận nhầm lẫn (FAIL là lớp dương, vì việc của judge là *tìm* lỗi):

| | tp | fp | fn | tn | Tỉ lệ FAIL quan sát → hiệu chỉnh Rogan-Gladen |
|---|---|---|---|---|---|
| tone_ok | 24 | 4 | 6 | 66 | 0.28 → 0.30 |
| helpful | 9 | 0 | 21 | 70 | 0.09 → 0.30 |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 1 | tone H-008 "Em đã hoàn tiền cho anh rồi nha…" | PASS | FAIL | Người | Xưng "em", "nha" quá suồng sã với khách khiếu nại. Rubric thêm: *không xưng em/bạn, không dùng tiểu từ thân mật (nha, nhé) với khách*. |
| 2 | tone H-029 "Dạ, vui lòng chờ… không cần nhắn thêm." | PASS | FAIL | Người | Judge bị đánh lừa bởi "Dạ, vui lòng" ở đầu câu; phần sau mang giọng ra lệnh. Rubric thêm: *chấm cả câu, câu ra lệnh/cấm khách liên hệ là FAIL dù mở đầu lịch sự*. |
| 3 | tone H-051 "Dạ, LogiX đã refund 90.000đ…" | FAIL | PASS | Người | Style guide CS LogiX cho phép từ "refund". Rubric sửa: *thuật ngữ trong danh sách cho phép (refund, ship, voucher) không bị trừ*. |
| 4 | tone H-081 "Dạ, đơn O-107 chưa đủ điều kiện hoàn…" | FAIL | PASS | **Judge** | Ghi chú dữ liệu: nhãn người sai do đọc nhầm ticket. Hành động: sửa nhãn người, ghi vào changelog nhãn; không sửa rubric. |
| 5 | tone H-063 "Dạ, LogiX đã hoàn 20.000đ và sẽ hoàn thêm…" | PASS | FAIL | Người | Hứa "sẽ hoàn thêm" ngoài kết quả hệ thống — đây là lỗi nội dung, không phải giọng văn. Hành động: tách khỏi rubric tone, bắt bằng code (reply chỉ được nói số có trong ledger, FM-08). |
| 6 | tone H-042 "Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ." | FAIL | PASS | Người | Judge phạt vì thiếu câu xin lỗi. Rubric sửa: *ngắn gọn, đủ ý không bị trừ; xin lỗi không bắt buộc khi đã giải quyết xong*. |
| 7 | helpful HL-015 "Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ." | PASS | FAIL | Người | Ledger ghi 40.000đ — reply nói sai số tiền. Judge chỉ đọc chữ, không thấy ledger nên không thể bắt. |
| 8 | helpful HL-016 / HL-043 / HL-090 (reply dài, xin lỗi lặp nhiều lần) | PASS | FAIL | Người | Judge thiên vị câu dài, nhiều lời xin lỗi (verbosity bias); cả ba đều nói số tiền khác ledger (vd HL-090 nói 155.000đ, ledger 120.000đ). |
| 9 | helpful HL-047 "Ok bạn, đơn O-515 xử lý rồi nhé." | PASS | FAIL | Người | Không nói kết quả, không nói số tiền — vô ích với khách, nhưng judge cho qua. |

## Kết luận
- **Loại `helpful`**: κ = 0.375 và recall = 0.30 — judge bỏ sót 21/30 reply mà người đánh FAIL (fn = 21), dù precision = 1.0 (fp = 0). Một judge "không bao giờ báo nhầm nhưng bỏ sót 70% lỗi" mà làm gate thì sẽ cho merge gần hết bản lỗi. Đọc 21 ca fn: 18 ca là reply nói **số tiền khác ledger** (ghi chú "ledger ghi …"), tức FM-08; judge không có ledger trong input nên về nguyên tắc không thể chấm đúng. Phần còn lại là reply dài xin lỗi (verbosity bias) và reply "Ok bạn… xử lý rồi" không có thông tin. Tiêu chí "đúng số tiền" phải chấm bằng **code** (so reply với ledger — metric FM-08 ở M3), không bằng judge.
- **Dùng `tone_ok`** có điều kiện: đạt cả 3 floor (κ 0.757, P 0.857, R 0.80), nhưng vẫn bỏ sót 6/30 lỗi giọng văn (xưng hô suồng sã, emoji, mất dấu) và phạt nhầm 4 ca (refund, thiếu xin lỗi, lặp "Dạ"). Chỉ dùng làm metric non-blocking cho chất lượng giọng văn và báo cáo tỉ lệ lỗi đã hiệu chỉnh Rogan-Gladen (0.28 → 0.30), không dùng cho tiền hay approval.
- Rủi ro còn lại: judge chỉ được kiểm trên dữ liệu replay đã công khai (100 dòng mỗi tiêu chí); các sửa rubric ở trên chưa được đo lại. Cần nhãn người mới (held-out) và chạy lại calibration sau khi sửa rubric trước khi tin con số κ/P/R. Một nhãn người đã được xác nhận là sai (H-081), nên bản thân nhãn người cũng cần kiểm tra chéo.