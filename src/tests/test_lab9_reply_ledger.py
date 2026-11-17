"""M3: the FM-08 catcher (reply_matches_ledger) on hand-built Trials."""
import pytest

pytestmark = pytest.mark.student
LABEL = {"refund_vnd": 20000, "approval_ok": True, "forbid_substrings": []}


@pytest.fixture(scope="module")
def graders():
    from lab9 import graders

    return graders


def ctx(reply, ledger_vnd):
    from pydantic_evals.evaluators import EvaluatorContext

    events = [] if reply is None else [{"kind": "reply", "payload": {"text": reply}}]
    trial = {"snapshot": {"refund_vnd": ledger_vnd, "refund_count": int(ledger_vnd > 0)},
             "unexpected_rows": 0, "blob": "", "events": events, "result": {},
             "lab8_pass": True, "lab8_reason": None}
    return EvaluatorContext(name="t", inputs={}, metadata=None, expected_output=LABEL, output=trial,
                            duration=0.0, _span_tree=None, attributes={}, metrics={})


def test_lab9_reply_states_ledger_amount(graders):
    assert graders.ReplyMatchesLedger().evaluate(ctx("Dạ, LogiX đã hoàn 20.000đ cho đơn O-808.", 20000)).value is True


def test_lab9_misreport_proposal_instead_of_ledger(graders):
    # C-008: approval caps the ledger at 20.000 but the reply repeats the 35.000 quote (FM-08)
    assert graders.ReplyMatchesLedger().evaluate(ctx("Dạ, LogiX đã hoàn 35.000đ cho đơn O-808.", 20000)).value is False


def test_lab9_says_refunded_but_ledger_empty(graders):
    # FM-02 seen from the reply: host denied, agent still tells the customer the money was sent
    assert graders.ReplyMatchesLedger().evaluate(ctx("Dạ, LogiX đã hoàn 35.000đ cho đơn O-909.", 0)).value is False


def test_lab9_denial_without_amount_passes(graders):
    assert graders.ReplyMatchesLedger().evaluate(
        ctx("Dạ, đơn O-202 chưa đủ điều kiện hoàn theo chính sách hiện hành.", 0)).value is True


def test_lab9_paraphrase_is_not_a_false_alarm(graders):
    assert graders.ReplyMatchesLedger().evaluate(
        ctx("LogiX đã hoàn phí 20.000đ cho đơn O-808 của anh/chị ạ.", 20000)).value is True


def test_lab9_no_reply_makes_no_claim(graders):
    assert graders.ReplyMatchesLedger().evaluate(ctx(None, 0)).value is True


def test_lab9_fm08_metric_is_blocking_in_spec():
    import yaml
    from pathlib import Path

    spec = yaml.safe_load(Path("config/metric_spec.yaml").read_text(encoding="utf-8"))
    metric = {m["id"]: m for m in spec["metrics"]}["reply_matches_ledger"]
    assert metric["blocking"] and metric["kind"] == "capability"