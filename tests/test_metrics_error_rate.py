from app import metrics


def test_snapshot_reports_error_rate_pct(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 8)
    monkeypatch.setattr(metrics, "ERRORS", {"RuntimeError": 2})

    snapshot = metrics.snapshot()

    assert snapshot["error_rate_pct"] == 20.0


def test_snapshot_reports_zero_error_rate_without_requests(monkeypatch) -> None:
    monkeypatch.setattr(metrics, "TRAFFIC", 0)
    monkeypatch.setattr(metrics, "ERRORS", {})

    assert metrics.snapshot()["error_rate_pct"] == 0.0
