"""Детерминированная двойная запись. Ядро мира: без внешних зависимостей."""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable
from closebench.strings import T

def D(x) -> Decimal:
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

ASSET, LIAB, EQUITY, INCOME, EXPENSE = "asset", "liability", "equity", "income", "expense"
DEBIT_NORMAL = {ASSET, EXPENSE}

@dataclass(frozen=True)
class Account:
    code: str
    name: str
    type: str

@dataclass(frozen=True)
class Line:
    account: str
    debit: Decimal = Decimal("0.00")
    credit: Decimal = Decimal("0.00")

@dataclass
class Entry:
    eid: str
    date: str          # YYYY-MM-DD
    memo: str
    lines: list[Line]
    source: str = "manual"      # manual | ap | ar | bank | accrual | payroll
    ref: str = ""               # номер документа
    tags: dict = field(default_factory=dict)

    def total_debit(self) -> Decimal:
        return sum((l.debit for l in self.lines), Decimal("0.00"))

    def total_credit(self) -> Decimal:
        return sum((l.credit for l in self.lines), Decimal("0.00"))

    def is_balanced(self) -> bool:
        return self.total_debit() == self.total_credit()

class Ledger:
    def __init__(self, accounts: Iterable[Account], lang: str = "en"):
        self.accounts: dict[str, Account] = {a.code: a for a in accounts}
        self.entries: list[Entry] = []
        self.lang = lang            # язык сообщений об ошибках проводки
        self._seq = 0

    def next_id(self, prefix="JE") -> str:
        self._seq += 1
        return f"{prefix}{self._seq:05d}"

    def post(self, entry: Entry) -> str:
        if not entry.lines:
            raise ValueError(T(self.lang, "ledger.no_lines"))
        for l in entry.lines:
            if l.account not in self.accounts:
                raise ValueError(T(self.lang, "ledger.unknown_account", account=l.account))
            if l.debit < 0 or l.credit < 0:
                raise ValueError(T(self.lang, "ledger.negative"))
            if l.debit > 0 and l.credit > 0:
                raise ValueError(T(self.lang, "ledger.both_sides"))
        if not entry.is_balanced():
            raise ValueError(T(self.lang, "ledger.unbalanced",
                               d=entry.total_debit(), c=entry.total_credit()))
        self.entries.append(entry)
        return entry.eid

    def in_period(self, start: str, end: str) -> list[Entry]:
        return [e for e in self.entries if start <= e.date <= end]

    def balance(self, code: str, upto: str | None = None) -> Decimal:
        acc = self.accounts[code]
        bal = Decimal("0.00")
        for e in self.entries:
            if upto and e.date > upto:
                continue
            for l in e.lines:
                if l.account == code:
                    bal += l.debit - l.credit
        return bal if acc.type in DEBIT_NORMAL else -bal

    def trial_balance(self, upto: str) -> list[dict]:
        rows = []
        for code, acc in sorted(self.accounts.items()):
            raw = Decimal("0.00")
            for e in self.entries:
                if e.date > upto:
                    continue
                for l in e.lines:
                    if l.account == code:
                        raw += l.debit - l.credit
            if raw == 0:
                continue
            rows.append({"code": code, "name": acc.name, "type": acc.type,
                         "debit": raw if raw > 0 else Decimal("0.00"),
                         "credit": -raw if raw < 0 else Decimal("0.00")})
        return rows

    def tb_totals(self, upto: str) -> tuple[Decimal, Decimal]:
        rows = self.trial_balance(upto)
        return (sum((r["debit"] for r in rows), Decimal("0.00")),
                sum((r["credit"] for r in rows), Decimal("0.00")))

    def pnl(self, start: str, end: str) -> dict:
        income = expense = Decimal("0.00")
        for e in self.in_period(start, end):
            for l in e.lines:
                t = self.accounts[l.account].type
                if t == INCOME:
                    income += l.credit - l.debit
                elif t == EXPENSE:
                    expense += l.debit - l.credit
        return {"income": income, "expense": expense, "net": income - expense}
