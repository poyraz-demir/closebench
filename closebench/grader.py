"""Программная награда. Никаких рубрик и оценок человеком."""
from __future__ import annotations
from decimal import Decimal
from closebench.ledger import D

def _adj_entries(world, session):
    return [e for e in world.ledger.entries if e.eid in set(session.posted)]

# Экономически эквивалентные счета: ошибка в выборе внутри группы — не ошибка по сути.
EQUIV = [
    {"6900", "6300"},            # прочие расходы / профуслуги
    {"2500", "2000"},            # межкомпанийные / кредиторка
    {"2400", "2000"},            # доходы будущих периодов / кредиторка
    {"1300", "1200"},            # расходы будущих периодов / запасы
    {"6700", "6900"},            # курсовые разницы / прочие расходы
    {"2100", "2000"},            # начисленные обязательства / кредиторка
    {"2200", "2100"},            # зарплата к выплате / начисленные обязательства
    {"6600", "6900"},            # связь и охрана / прочие расходы
]

def _same(a: str, b: str) -> bool:
    if a == b:
        return True
    return any(a in grp and b in grp for grp in EQUIV)

def _matches(e, want_dr, want_cr, amount, strict=True) -> bool:
    amt = D(amount)
    eq = (lambda a, b: a == b) if strict else _same
    dr = [l for l in e.lines if l.debit == amt and eq(l.account, want_dr)]
    cr = [l for l in e.lines if l.credit == amt and eq(l.account, want_cr)]
    return bool(dr and cr)

def grade(world, session) -> dict:
    adjs = _adj_entries(world, session)
    found, partial, missed = [], [], []
    matched_eids = set()
    for err in world.errors:
        fix = err.fix
        exact = near = None
        for e in adjs:
            if e.eid in matched_eids:          # одна проводка закрывает максимум одну ошибку
                continue
            if not (fix["period"][0] <= e.date <= fix["period"][1]):
                continue
            if fix["type"] not in ("require_entry", "require_reversal"):
                continue
            if _matches(e, fix["debit_account"], fix["credit_account"], fix["amount"], strict=True):
                exact = e.eid
                break
            if near is None and _matches(e, fix["debit_account"], fix["credit_account"],
                                         fix["amount"], strict=False):
                near = e.eid
        if exact:
            found.append(err.err_id); matched_eids.add(exact)
        elif near:
            partial.append(err.err_id); matched_eids.add(near)
        else:
            missed.append(err.err_id)

    d, c = world.ledger.tb_totals(world.period_end)
    tb_balanced = d == c

    # «ничего лишнего»: корректировки, не сопоставленные ни одной ошибке
    spurious = [e.eid for e in adjs if e.eid not in matched_eids]

    total = len(world.errors)
    score = (len(found) + 0.5 * len(partial)) / total if total else 0.0
    penalty = 0.1 * len(spurious)
    passed = (len(found) + len(partial) == total) and tb_balanced and not spurious

    return {
        "passed": passed,
        "score": round(max(0.0, score - penalty), 3),
        "found": found, "partial": partial, "missed": missed,
        "spurious_entries": spurious,
        "tb_balanced": tb_balanced,
        "adjustments_posted": len(adjs),
        "tool_calls": getattr(session, "external_calls", len(session.calls)),
    }
