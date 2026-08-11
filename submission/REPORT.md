# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (20 log records, 20 correlation ID duy nhất, 0 field thiếu)
- Tổng số traces: 26+ (26 correlation ID duy nhất trong `data/logs.jsonl`, xác nhận khớp với Langfuse qua API)
- Số PII leak còn lại: 0
- Link/đường dẫn dashboard: TODO — điền đường dẫn ảnh `submission/evidence/dashboard.png` sau khi chụp

## 3. Logging và tracing

- Evidence correlation ID:
- Evidence PII redaction:
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

## 4. Prompt versioning

- Prompt name: day13-chat
- Version/label baseline: version 1, label `baseline` — xác nhận qua trace metadata (`prompt_source: langfuse`)
- Version/label candidate: version 2, label `candidate` — xác nhận qua trace metadata (`prompt_source: langfuse`)
- Trace ID của mỗi version:
  - baseline: `44e8d73462e8b59f241b76ff025ed2a8` — https://cloud.langfuse.com/project/cmso2gkcj03m1ad0izhq8u4qf/traces/44e8d73462e8b59f241b76ff025ed2a8
  - candidate: `9aaa2a1d6641b5106098c0a9085e95a8` — https://cloud.langfuse.com/project/cmso2gkcj03m1ad0izhq8u4qf/traces/9aaa2a1d6641b5106098c0a9085e95a8
- Bằng chứng đổi label hoặc rollback: đã đổi label `production` sang version 2, xác nhận qua trace `b237d36d2f582c0e1c1d50442f25a31e` (prompt_version=2), sau đó rollback `production` về version 1, xác nhận qua trace `e47071e1377588ecd5b04cbf9033cef7` (prompt_version=1). Cả 2 trace lấy được bằng cách gọi `/chat` ngay sau khi đổi label trên Langfuse và đợi hết TTL cache prompt (60s, xem `app/prompt_management.py`).
  - promote → v2: https://cloud.langfuse.com/project/cmso2gkcj03m1ad0izhq8u4qf/traces/b237d36d2f582c0e1c1d50442f25a31e
  - rollback → v1: https://cloud.langfuse.com/project/cmso2gkcj03m1ad0izhq8u4qf/traces/e47071e1377588ecd5b04cbf9033cef7
  - TODO: chụp ảnh 4 trace trên (baseline, candidate, promote, rollback) lưu vào `submission/evidence/`

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ — 6/6 panel (latency, traffic, errors, cost, tokens, quality) đúng contract `config/dashboard.yaml`
- Evidence dashboard: TODO — chụp ảnh dashboard (đủ 6 panel, time range 60 phút, threshold/SLO line) lưu vào `submission/evidence/dashboard.png`
- SLO đã chọn và lý do (dựa trên baseline đo được từ `data/logs.jsonl`, xem `config/slo.yaml`):
  - `latency_p95_ms`: objective 2000ms, target 99.5%/28d — baseline đo được ~1.1–1.3s, đặt margin để dò degrade thật
  - `error_rate_pct`: objective 2%, target 99.0%/28d — baseline 0% lỗi, giữ ngưỡng an toàn thay vì 0% cứng
  - `daily_cost_usd`: objective 0.3 USD, target 100%/28d — baseline quan sát ~0.13 USD, nhân ~2-2.5 lần làm margin
  - `quality_score_avg`: objective 0.8, target 95.0%/28d — baseline trung bình 0.88 trên 30 request
- Alert rules và runbook (`config/alert_rules.yaml`, chi tiết `docs/alerts.md`):
  - `SlowResponsesForUsers` (warning) — p95 latency > 2000ms/5m, symptom: người dùng chờ lâu
  - `ElevatedRequestFailureRate` (critical) — error rate > 2%/5m, symptom: một phần request không có phản hồi
  - `DegradedAnswerQuality` (warning) — mean quality_score < 0.8/15m, symptom: câu trả lời kém liên quan/hữu ích hơn

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
