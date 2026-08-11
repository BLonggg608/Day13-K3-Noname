# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: K3 - Day 13
- Repository URL: https://github.com/BLonggg608/Day13-K3-Noname
- Commit SHA cuối: `fc8b3d3bc99011e7a85dcd53e11ef3c70ae89a63`
- Thành viên và vai trò:
  - Thành viên Trần Hà Bảo Long - 2A202601189: Logging & Middleware
  - Thành viên Đào Quốc Đại - 2A202601285: Security & Compliance
  - Thành viên Nguyễn Quang Minh - 2A202601955: Metrics & Alerting
  - Thành viên Đặng Trần Trung Dũng - 2A202601785: QA & Incident Analyst

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 sau khi tạo lại log sạch.
- Tổng số traces: Tối thiểu 10 traces, evidence tại `submission/evidence/traces_list.png`.
- Số PII leak còn lại: 0 trong lần chạy validator đã thực hiện.
- Link/đường dẫn dashboard: `config/dashboard.yaml`; runtime screenshot chưa cập nhật.

## 3. Logging và tracing

- Evidence Correlation ID: Response thành công giữ `x-request-id: test-cp1-001`; challenge có các ID `req-46b8548b`, `req-e285eb15`, `req-2bfbcae3`, `req-0e70d3fb`, `req-c8fefe3c`.
- Evidence PII redaction: Log chứa `user_id_hash` thay vì user ID gốc; validator ghi nhận `Potential PII leaks detected: 0`.
- Evidence trace waterfall: `submission/evidence/trace_waterfall.png`.
- Giải thích một span đáng chú ý: `app.mock_rag.retrieve()` tạo blocking delay 2.5 giây khi incident `rag_slow` được bật; `response_sent` ghi nhận latency khoảng 2650 ms.

## 4. Prompt versioning

- Prompt name: `day13-chat` theo cấu hình mặc định.
- Version/label baseline: Evidence `submission/evidence/prompt_version1.png` và `submission/evidence/baseline_trace.png`.
- Version/label candidate: Evidence `submission/evidence/prompt_version2.png` và `submission/evidence/candidate_trace.png`.
- Trace ID của mỗi version: Có trong các ảnh trace tương ứng.
- Bằng chứng đổi label hoặc rollback: `submission/evidence/version2_production.png` và `submission/evidence/version1_production_rollback.png`.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ - 6/6 panel có trong dashboard contract.
- Evidence dashboard: `submission/evidence/dashboard-validator.txt`; contract validator đạt 6/6 panel.
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
- Trace ID liên quan: Đối chiếu trong `submission/evidence/trace_waterfall.png`; correlation ID được dùng để truy vết log.
- Log line/correlation ID liên quan: `req-46b8548b`, `req-e285eb15`, `req-2bfbcae3`, `req-0e70d3fb`, `req-c8fefe3c`.
- Root cause: `app.mock_rag.retrieve()` gọi `time.sleep(2.5)` khi `STATE["rag_slow"]` là `True`, tạo blocking delay trong retrieval path.
- Fix action: Tắt incident bằng `python scripts/inject_incident.py --disable` sau khi hoàn tất challenge.
- Preventive measure: Theo dõi P95 latency, instrument retrieval span, dùng Correlation ID để liên kết Metrics - Traces - Logs và cảnh báo khi P95 vượt SLO.
- Evidence chi tiết: `submission/evidence/challenge-runtime.txt`.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ, commit/PR tương ứng và evidence đã hoàn thành.

| Thành viên   | Phạm vi việc                                        | Commit/PR     | Evidence đã hoàn thành                                        |
| ------------ | --------------------------------------------------- | ------------- | ------------------------------------------------------------- |
| Đại | PII scrubbing và Security & Compliance | `3b6c9b7` (`DaoQuocDai`) | PII leak 0 trong validator |
| Long | Middleware, Correlation ID, log metadata enrichment | `58034b8`, `a91ded7`, `f1a9bf3` (`Blonggg608`) | CP1, `validate-logs-final.txt` 100/100 |
| Dũng | Challenge config, Dashboard và runtime refresh | `a0e8615`, `8b92616`, `5c076f8` (`dungdunno16`) | Dashboard 6/6, challenge configuration/evidence |
| Minh | Metrics, Dashboard và CP2 integration | `46ccbaa`, `7116270` (`minhNQ`) | Metrics, SLO/alerts và CP2 evidence |
