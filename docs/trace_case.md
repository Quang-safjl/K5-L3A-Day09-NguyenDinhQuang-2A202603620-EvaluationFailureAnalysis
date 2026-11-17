# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi nhóm 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, trace run ID `R-seeded_regression-C-002-s11` (cùng lỗi trên `swarm C-002@55`, run ID `R-swarm-C-002-s55`) |
| Triệu chứng | Grader Lab 8 FAIL: `status resolved != denied`. Ledger ghi 20.000 cho C-002 trong khi nhãn là 0 / `denied`; reply nói "Dạ, LogiX đã hoàn 20.000đ cho đơn O-202." — reply khớp ledger nhưng cả hai đều sai |
| Bước sai đầu tiên | Event 3 `model_override`: `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event 1 `handoff` chỉ có tool đọc, `facts` rỗng (đúng). Event 2 `investigator` đọc DB: đơn O-202 `delay_days = 2` (đúng, < 3 ngày nên không được hoàn). Event 3 ghi đè 2 bằng số 5 khách viết trong ticket; từ đó event 4 `quote` ra 20.000 và host ghi ledger theo quote sai |
| Failure mode | FM-03 ticket_trust (layer model/prompt) |
| Đối chứng | `fixed C-002@11`: không có event `model_override`; event 3 `quote` = 0 (`no_entitlement`), reply "chưa đủ điều kiện", ledger 0, grader PASS |
| Regression test | `src/tests/test_lab9_trace_case.py`: `test_lab9_trace_case_c002_seeded_regression_overrides_db_delay` (assert event đầu tiên sau `handoff`, `investigator` là `model_override` với `delay_days` khác DB, trial fail) và `test_lab9_trace_case_c002_fixed_keeps_db_fact` (không có `model_override`, trial pass). Đã chạy: fail-đúng trên variant lỗi, pass trên `fixed`. Metric `db_fact_kept` trong `metric_spec.yaml` bắt cùng lỗi này ở mức eval set |
| Chưa chắc chắn | Trace không cho biết *vì sao* model chọn tin ticket (prompt hay seed); với variant `quiet_override` cùng lỗi xảy ra mà không có event `model_override`, nên test dựa vào event sẽ bỏ sót — phải dựa thêm vào so sánh quote với `delay_days` của DB và ledger với nhãn |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
