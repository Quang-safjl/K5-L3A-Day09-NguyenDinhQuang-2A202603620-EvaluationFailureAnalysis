"""Regression test for docs/trace_case.md: C-002@11, first wrong step = model_override (FM-03)."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.config_loader import repo_path
from lab8.metrics import trial_pass
from lab9.variant_agent import make_shape
from lab9.variants import VARIANTS

pytestmark = pytest.mark.student

WORLD = load_json(repo_path("data", "public_world_state.json"))
CLAIMS = {c["claim_id"]: c for c in load_jsonl(repo_path("data", "public_claims.jsonl"))}


def _run(variant: str, tmp_path: Path, claim_id: str = "C-002", seed: int = 11):
    store = tmp_path / f"{variant}.sqlite"
    init_store(store, WORLD, list(CLAIMS.values())).close()
    started = time.time()
    result = make_shape(variant, VARIANTS[variant])(claim_id, seed=seed, store_path=str(store))
    events = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))["events"]
    conn = connect(store)
    try:
        ok, why = trial_pass(result.as_dict(), CLAIMS[claim_id]["expected"], conn, started_at=started)
    finally:
        conn.close()
    return events, ok, why


def test_lab9_trace_case_c002_seeded_regression_overrides_db_delay(tmp_path):
    events, ok, why = _run("seeded_regression", tmp_path)
    kinds = [e["kind"] for e in events]
    first_wrong = kinds.index("model_override")
    assert kinds[:first_wrong] == ["handoff", "investigator"]          # steps before it are correct
    db_delay = events[1]["payload"]["lookup_order"]["order"]["delay_days"]
    assert events[first_wrong]["payload"]["delay_days"] != db_delay    # ticket number replaced the DB fact
    assert not ok and "denied" in why


def test_lab9_trace_case_c002_fixed_keeps_db_fact(tmp_path):
    events, ok, why = _run("fixed", tmp_path)
    assert "model_override" not in [e["kind"] for e in events]
    assert ok, why