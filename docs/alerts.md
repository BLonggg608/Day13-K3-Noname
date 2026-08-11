# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: SlowResponsesForUsers
- Severity: warning
- SLI/SLO liên quan: `latency_p95_ms` (objective ≤ 2000ms, target 99.5% trong 28d)
- Điều kiện và thời gian duy trì: p95 của `response_sent.latency_ms` > 2000ms, duy trì liên tục 5 phút
- Ảnh hưởng tới người dùng: Người dùng phải chờ câu trả lời lâu hơn bình thường, trải nghiệm chat bị chậm/đơ
- Ba bước kiểm tra đầu tiên:
  1. Xem panel Latency trên dashboard để xác nhận p95/p99 tăng và từ thời điểm nào
  2. Mở trace của các request chậm gần nhất, xem span nào (RAG retrieval, LLM call, ...) chiếm phần lớn thời gian
  3. Kiểm tra traffic cùng thời điểm (panel Traffic) để loại trừ nguyên nhân do tăng tải đột biến
- Mitigation tạm thời: Giảm concurrency/rate limit tạm thời, hoặc chuyển sang fallback response nhanh hơn (rút gọn context/số doc retrieve) trong khi điều tra nguyên nhân gốc
- Owner: on-call-backend

## Alert 2

- Tên: ElevatedRequestFailureRate
- Severity: critical
- SLI/SLO liên quan: `error_rate_pct` (objective ≤ 2%, target 99.0% trong 28d)
- Điều kiện và thời gian duy trì: (`request_failed` / `request_received`) > 2%, duy trì liên tục 5 phút
- Ảnh hưởng tới người dùng: Một phần yêu cầu của người dùng không nhận được câu trả lời (lỗi/timeout), có thể mất dữ liệu hội thoại
- Ba bước kiểm tra đầu tiên:
  1. Xem panel Errors để biết `error_type` nào chiếm đa số (timeout, exception, upstream lỗi...)
  2. Lọc log theo `correlation_id` của các request lỗi gần nhất để xem chi tiết stack/nguyên nhân
  3. Kiểm tra trace tương ứng để xác định lỗi xảy ra ở bước nào trong pipeline (retrieval, LLM call, post-processing)
- Mitigation tạm thời: Bật retry có giới hạn cho lỗi tạm thời (transient), hoặc rollback về prompt/version ổn định gần nhất nếu lỗi mới xuất hiện sau một lần đổi label/deploy
- Owner: on-call-backend

## Alert 3

- Tên: DegradedAnswerQuality
- Severity: warning
- SLI/SLO liên quan: `quality_score_avg` (objective ≥ 0.8, target 95.0% trong 28d)
- Điều kiện và thời gian duy trì: mean(`response_sent.quality_score`) < 0.8, duy trì liên tục 15 phút
- Ảnh hưởng tới người dùng: Câu trả lời kém liên quan hơn, ngắn hơn hoặc bị che (PII redaction) nhiều hơn bình thường, giảm độ hữu ích của trợ lý
- Ba bước kiểm tra đầu tiên:
  1. Xem panel Quality để xác nhận xu hướng giảm và mốc thời gian bắt đầu
  2. Đối chiếu với `docs/PROMPT_VERSIONING.md` xem có vừa đổi `prompt_label`/`prompt_version` trùng thời điểm không
  3. Đọc mẫu vài `response_sent.payload.answer_preview` để xem câu trả lời có bị cắt ngắn, không liên quan, hoặc bị redact nhiều bất thường không
- Mitigation tạm thời: Rollback prompt về version/label ổn định trước đó nếu nguyên nhân là do đổi prompt; nếu do dữ liệu retrieval kém thì tạm mở rộng số lượng doc retrieve
- Owner: on-call-backend
