"""Invariants every closebench release must keep.

Run with:  python -m pytest -q
"""
from decimal import Decimal
import hashlib
import json

import pytest

from closebench.world import World
from closebench.tools import Session
from closebench.grader import grade

LANGS = ["en", "ru"]
HARD_SEEDS = list(range(1, 11))
ABSENCE_SEEDS = list(range(1001, 1011))


def _snapshot_hash(w: World) -> str:
    payload = json.dumps(w.snapshot(), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def _numbers(w: World):
    """Everything about a world except its text."""
    return (
        [(e.date, [(l.account, str(l.debit), str(l.credit)) for l in e.lines])
         for e in w.ledger.entries],
        sorted(w.chosen),
        dict(w.gap_month),
        [e.fix for e in w.errors],
    )


@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("seed", HARD_SEEDS + ABSENCE_SEEDS)
def test_same_seed_same_world(lang, seed):
    a = World(seed=seed, lang=lang, difficulty=_mode(seed)).build()
    b = World(seed=seed, lang=lang, difficulty=_mode(seed)).build()
    assert _snapshot_hash(a) == _snapshot_hash(b)


@pytest.mark.parametrize("seed", HARD_SEEDS + ABSENCE_SEEDS)
def test_locale_changes_text_only(seed):
    ru = World(seed=seed, lang="ru", difficulty=_mode(seed)).build()
    en = World(seed=seed, lang="en", difficulty=_mode(seed)).build()
    assert _numbers(ru) == _numbers(en)


@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("seed", HARD_SEEDS + ABSENCE_SEEDS)
def test_books_are_sane(lang, seed):
    w = World(seed=seed, lang=lang, difficulty=_mode(seed)).build()
    debit, credit = w.ledger.tb_totals(w.period_end)
    assert debit == credit, "trial balance must balance"
    assert w.ledger.balance("1000", w.period_end) >= 0, "cash never negative"
    assert w.ledger.balance("1200", w.period_end) >= 0, "inventory never negative"
    assert len(w.errors) == len(w.chosen)


@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("seed", HARD_SEEDS + ABSENCE_SEEDS)
def test_empty_session_scores_zero(lang, seed):
    w = World(seed=seed, lang=lang, difficulty=_mode(seed)).build()
    res = grade(w, Session(w))
    assert res["passed"] is False
    assert res["score"] == 0.0
    assert res["spurious_entries"] == []


@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("seed", HARD_SEEDS + ABSENCE_SEEDS)
def test_oracle_scores_one(lang, seed):
    w = World(seed=seed, lang=lang, difficulty=_mode(seed)).build()
    s = Session(w)
    for err in w.errors:
        fix = err.fix
        s.post_entry(w.period_end, err.err_id, [
            {"account": fix["debit_account"], "debit": fix["amount"]},
            {"account": fix["credit_account"], "credit": fix["amount"]},
        ])
    res = grade(w, s)
    assert res["passed"] is True
    assert res["score"] == 1.0
    assert res["missed"] == []
    assert res["spurious_entries"] == []


@pytest.mark.parametrize("seed", HARD_SEEDS + ABSENCE_SEEDS)
def test_no_amount_collisions(seed):
    """One posted entry must never be able to satisfy two planted errors."""
    w = World(seed=seed, difficulty=_mode(seed)).build()
    sig = [(e.fix["debit_account"], e.fix["credit_account"], str(Decimal(e.fix["amount"])))
           for e in w.errors]
    assert len(sig) == len(set(sig))


def test_extra_entry_is_penalised():
    w = World(seed=1).build()
    s = Session(w)
    s.post_entry(w.period_end, "unjustified", [
        {"account": "6900", "debit": "123.45"},
        {"account": "1000", "credit": "123.45"},
    ])
    res = grade(w, s)
    assert res["spurious_entries"], "an unmatched adjustment must be reported"
    assert res["passed"] is False


def test_equivalent_account_gets_partial_credit():
    # find any hard-mode seed that plants the intercompany error
    w = err = None
    for seed in range(1, 80):
        cand = World(seed=seed).build()
        hit = [e for e in cand.errors if e.kind == "intercompany_mismatch"]
        if hit:
            w, err = cand, hit[0]
            break
    assert err is not None, "no seed in 1..79 plants intercompany_mismatch"
    s = Session(w)
    s.post_entry(w.period_end, "ic via professional services", [
        {"account": "6300", "debit": err.fix["amount"]},     # 6300 ~ 6900
        {"account": "2500", "credit": err.fix["amount"]},
    ])
    res = grade(w, s)
    assert err.err_id in res["partial"]
    assert err.err_id not in res["missed"]
    assert res["spurious_entries"] == []


def _mode(seed: int) -> str:
    return "absence" if seed >= 1000 else "hard"
