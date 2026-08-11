# Alert và Runbook Day 13

## Alert 1

- Tên: `api_latency_p95_high`
- Severity: warning
- SLI/SLO: `latency_p95_ms <= 3000`
- Điều kiện: P95 latency > 3000 ms trong 10 phút.
- Ảnh hưởng: request chậm, timeout hoặc trải nghiệm người dùng giảm.
- Ba kiểm tra đầu tiên: xem latency panel; tìm trace chậm; đối chiếu log theo correlation ID.
- Mitigation: tắt incident practice, kiểm tra retrieval/tool, giảm concurrency nếu cần.
- Owner: Metrics & Alerting

## Alert 2

- Tên: `api_error_rate_high`
- Severity: critical
- SLI/SLO: `error_rate_pct <= 2`
- Điều kiện: error rate > 2% trong 5 phút.
- Ảnh hưởng: request thất bại và chức năng bị gián đoạn.
- Ba kiểm tra đầu tiên: xem error breakdown; tìm `request_failed`; đối chiếu correlation ID với trace.
- Mitigation: rollback prompt/deploy gần nhất, tắt incident, chuyển fallback nếu có.
- Owner: Metrics & Alerting

## Alert 3

- Tên: `ai_cost_or_quality_breach`
- Severity: warning
- SLI/SLO: daily cost <= 2.5 USD và quality average >= 0.75.
- Điều kiện: daily cost > 2.5 USD hoặc quality average < 0.75 trong 15 phút.
- Ảnh hưởng: chi phí tăng hoặc chất lượng trả lời giảm.
- Ba kiểm tra đầu tiên: xem token/cost panel; kiểm tra output token bất thường; so sánh quality theo feature/model.
- Mitigation: giới hạn output tokens, tắt `cost_spike`, rollback prompt candidate.
- Owner: Metrics & Alerting

## Quy trình chung

1. Ghi nhận thời điểm, alert và phạm vi ảnh hưởng.
2. Dùng Metrics để xác định triệu chứng, Traces để tìm span bất thường và Logs để xác nhận nguyên nhân.
3. Thực hiện mitigation an toàn, sau đó xác nhận SLI trở về ngưỡng.
4. Lưu metric, trace ID, correlation ID và log line vào `submission/evidence/`.
