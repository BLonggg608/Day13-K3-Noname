# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: K3 - Day 13
- Repository URL: Chưa cập nhật
- Commit SHA cuối: Chưa cập nhật trước khi nộp bài
- Thành viên và vai trò:
  - Thành viên A: Logging & Middleware
  - Thành viên B: Security & Compliance
  - Thành viên C: Metrics & Alerting
  - Thành viên D: QA & Incident Analyst

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 sau khi tạo lại log sạch.
- Tổng số traces: Chưa xác minh trên Langfuse.
- Số PII leak còn lại: 0 trong lần chạy validator đã thực hiện.
- Link/đường dẫn dashboard: `config/dashboard.yaml`; runtime screenshot chưa cập nhật.

## 3. Logging và tracing

- Evidence Correlation ID: Response thành công giữ `x-request-id: test-cp1-001`; challenge có các ID `req-46b8548b`, `req-e285eb15`, `req-2bfbcae3`, `req-0e70d3fb`, `req-c8fefe3c`.
- Evidence PII redaction: Log chứa `user_id_hash` thay vì user ID gốc; validator ghi nhận `Potential PII leaks detected: 0`.
- Evidence trace waterfall: Chưa xác minh trên Langfuse.
- Giải thích một span đáng chú ý: `app.mock_rag.retrieve()` tạo blocking delay 2.5 giây khi incident `rag_slow` được bật; `response_sent` ghi nhận latency khoảng 2650 ms.

## 4. Prompt versioning

- Prompt name: `day13-chat` theo cấu hình mặc định.
- Version/label baseline: Chưa xác minh trên Langfuse.
- Version/label candidate: Chưa xác minh trên Langfuse.
- Trace ID của mỗi version: Chưa xác minh trên Langfuse.
- Bằng chứng đổi label hoặc rollback: Chưa có evidence Langfuse thật.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ - 6/6 panel có trong dashboard contract.
- Evidence dashboard: `submission/evidence/dashboard-validator.txt`; runtime screenshot chưa cập nhật.
- SLO đã chốt và lý do:
  - `latency_p95_ms`: mục tiêu không vượt 3000 ms, target 99.5%.
  - `error_rate_pct`: mục tiêu không vượt 2%, target 99.0%.
  - `daily_cost_usd`: mục tiêu không vượt 2.5 USD.
  - `quality_score_avg`: mục tiêu không thấp hơn 0.75.
- Alert rules và Runbook:
  - `api_latency_p95_high`: P95 latency > 3000 ms trong 10 phút.
  - `api_error_rate_high`: error rate > 2% trong 5 phút.
  - `ai_cost_or_quality_breach`: daily cost > 2.5 USD hoặc quality average < 0.75 trong 15 phút.
  - Cấu hình: `config/alert_rules.yaml`.
  - Runbook: `docs/alerts.md`.

## 6. Điều tra challenge

- Challenge ID: `day13-k3-observability-v1`
- Triệu chứng từ metrics: Khi bật `rag_slow`, client-observed latency tăng lên khoảng 5314.0-13290.4 ms, vượt threshold 2000 ms.
- Trace ID liên quan: Chưa xác minh trên Langfuse; correlation ID được dùng để truy vết log.
- Log line/correlation ID liên quan: `req-46b8548b`, `req-e285eb15`, `req-2bfbcae3`, `req-0e70d3fb`, `req-c8fefe3c`.
- Root cause: `app.mock_rag.retrieve()` gọi `time.sleep(2.5)` khi `STATE["rag_slow"]` là `True`, tạo blocking delay trong retrieval path.
- Fix action: Tắt incident bằng `python scripts/inject_incident.py --disable` sau khi hoàn tất challenge.
- Preventive measure: Theo dõi P95 latency, instrument retrieval span, dùng Correlation ID để liên kết Metrics - Traces - Logs và cảnh báo khi P95 vượt SLO.
- Evidence chi tiết: `submission/evidence/challenge-runtime.txt`.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ, commit/PR tương ứng và evidence đã hoàn thành.

| Thành viên | Phạm vi việc | Commit/PR | Evidence đã hoàn thành |
|---|---|---|---|
| Thành viên A | Middleware, Correlation ID, log metadata enrichment | Chưa cập nhật | CP1, `validate_logs.py` 100/100 |
| Thành viên B | PII scrubbing và Security & Compliance | Chưa cập nhật | PII leak 0 trong validator |
| Thành viên C | Langfuse, Metrics, SLO, Alert rules và Runbook | Chưa cập nhật | Alert rules và Runbook đã có; Langfuse evidence chưa xác minh |
| Thành viên D | Load test, Dashboard và Incident Analysis | Chưa cập nhật | Dashboard 6/6, challenge evidence |
