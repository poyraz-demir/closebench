"""Генератор мира: компания, 12 месяцев операций, документы, посаженные ошибки.
Детерминирован: один и тот же seed даёт побайтово одинаковый мир.

v2 (19.09.2026): 13 типов ошибок вместо 8, из них пять расчётных или бездокументных.
Каждый тип ошибки имеет «двойника»-пустышку: если тип не посажен, мир всё равно
показывает похожий документ или похожую законную операцию, поэтому состав задачи
нельзя прочитать по инвентарю документов.

v3 (21.09.2026): локали ru/en. Все пользовательские строки идут через
closebench.strings.T и НЕ трогают rng: для одного seed миры ru и en совпадают
по проводкам, суммам, датам, составу ошибок и gap_month — отличается только текст."""
from __future__ import annotations
import random, json, datetime as dt
from dataclasses import dataclass, asdict, field
from decimal import Decimal
from closebench.ledger import (Ledger, Account, Entry, Line, D,
                               ASSET, LIAB, EQUITY, INCOME, EXPENSE)
from closebench.strings import T, LANGS, month_label

# Коды и типы счетов — константа; наименования берутся из локали.
COA_CODES = [
    ("1000", ASSET), ("1100", ASSET), ("1200", ASSET), ("1300", ASSET),
    ("1500", ASSET), ("1590", ASSET),
    ("2000", LIAB), ("2100", LIAB), ("2200", LIAB), ("2300", LIAB),
    ("2400", LIAB), ("2500", LIAB),
    ("3000", EQUITY), ("3100", EQUITY),
    ("4000", INCOME),
    ("5000", EXPENSE), ("6000", EXPENSE), ("6100", EXPENSE), ("6200", EXPENSE),
    ("6300", EXPENSE), ("6400", EXPENSE), ("6500", EXPENSE), ("6600", EXPENSE),
    ("6700", EXPENSE), ("6800", EXPENSE), ("6900", EXPENSE),
]

def coa(lang: str = "en") -> list[Account]:
    """План счетов с наименованиями на языке `lang`."""
    return [Account(code, T(lang, f"coa.{code}"), typ) for code, typ in COA_CODES]

COA = coa("en")

@dataclass
class Document:
    doc_id: str
    kind: str            # vendor_invoice | bank_statement | contract | email | policy
    date: str
    title: str
    body: str
    meta: dict = field(default_factory=dict)

@dataclass
class PlantedError:
    err_id: str
    kind: str
    description: str     # истина для грейдера, агенту не показывается
    entry_ids: list[str]
    accounts: list[str]
    amount: str
    fix: dict            # машинно-проверяемое условие исправления

def eom(y, m):
    return (dt.date(y, m, 1) + dt.timedelta(days=32)).replace(day=1) - dt.timedelta(days=1)

def dim(y, m):
    return eom(y, m).day

class World:
    def __init__(self, seed: int, lang: str = "en", difficulty: str = "hard",
                 name: str | None = None, year: int = 2026, close_month: int = 11):
        if lang not in LANGS:
            raise ValueError(f"unsupported lang {lang!r}; expected one of {LANGS}")
        self.seed, self.lang, self.year, self.close_month = seed, lang, year, close_month
        self.name = name if name is not None else T(lang, "company")
        self.difficulty = difficulty
        self.rng = random.Random(seed)
        self.coa = coa(lang)
        self.ledger = Ledger(self.coa, lang=lang)
        self.documents: list[Document] = []
        self.errors: list[PlantedError] = []
        self.period_start = f"{year}-{close_month:02d}-01"
        self.period_end = eom(year, close_month).isoformat()
        self.chosen: set[str] = set()

    # ---------- базовые операции ----------
    def _t(self, key: str, **fmt) -> str:
        """Строка локали мира. Год подставляется всегда; при наличии `m` — и подпись месяца."""
        fmt.setdefault("y", self.year)
        if "m" in fmt:
            fmt.setdefault("mon", month_label(self.lang, fmt["m"]))
        return T(self.lang, key, **fmt)

    def _je(self, date, memo, pairs, source="manual", ref="", tags=None):
        lines = [Line(acc, D(dr), D(cr)) for acc, dr, cr in pairs]
        e = Entry(self.ledger.next_id(), date, memo, lines, source, ref, tags or {})
        self.ledger.post(e)
        return e.eid

    def _memo(self, plain: str, terse: str) -> str:
        """В hard-режиме проводка описана так, как в жизни: кодом документа, а не смыслом."""
        return terse if self.difficulty == "hard" else plain

    def _doc(self, *a, **kw):
        self.documents.append(Document(*a, **kw))

    # ---------- сборка ----------
    ERROR_KINDS = [
        "unrecorded_invoice",     # E1  счёт не проведён
        "duplicate_invoice",      # E2  счёт проведён дважды
        "capex_expensed",         # E3  ОС списано в расходы
        "prepaid_not_deferred",   # E4  годовая лицензия целиком в расходы
        "revenue_cutoff",         # E5  аванс признан выручкой
        "unrecorded_bank_fee",    # E6  комиссия банка не проведена
        "misclassified_expense",  # E7  расход не на тот счёт
        "intercompany_mismatch",  # E8  межкомпанийный разрыв
        "missing_recurring",      # E9  регулярное начисление пропущено (документа нет)
        "fx_revaluation",         # E10 валютная кредиторка не переоценена (расчёт)
        "depreciation_prorata",   # E11 амортизация нового ОС не начислена (расчёт по дням)
        "service_span_cutoff",    # E12 услуга через границу периода (расчёт по дням)
        "payroll_cutoff",         # E13 зарплата за 26–30 не начислена (расчёт, документа нет)
        "depreciation_stopped",   # E14 амортизация пропущена в одном месяце года
        "prepaid_amort_stopped",  # E15 списание страховки пропущено в одном месяце года
        "accrual_not_released",   # E16 резерв прошлого месяца не погашен при выплате
        "inventory_receipt_gap",  # E17 поступление товара пропущено в одном месяце года
    ]

    # Ошибки-отсутствия: ошибка есть только как пропуск в ряду, документа-улики нет.
    ABSENCE_KINDS = ["missing_recurring", "payroll_cutoff", "depreciation_stopped",
                     "prepaid_amort_stopped", "accrual_not_released", "inventory_receipt_gap"]

    def _choose(self):
        """Состав ошибок фиксируется ДО построения месяцев: часть ошибок — это
        отсутствие операции, а не лишняя операция, поэтому месяцы должны знать состав."""
        if self.difficulty == "absence":
            k = self.rng.choice([4, 5, 5, 6])
            self.chosen = set(self.rng.sample(self.ABSENCE_KINDS, k))
        else:
            k = self.rng.choice([6, 7, 7, 8, 8, 9])
            self.chosen = set(self.rng.sample(self.ERROR_KINDS, k))
        # Ключевое: пропуск прячется в СЛУЧАЙНОМ месяце года, а не в месяце закрытия.
        # Иначе задача решается механическим сравнением двух последних месяцев.
        self.gap_month = {kind: self.rng.randint(2, self.close_month)
                          for kind in self.ABSENCE_KINDS}
        # Пропуск прихода товара в первые месяцы законно объясняется стартовым
        # запасом, поэтому такая ошибка была бы несправедливой: прячем её позже.
        self.gap_month["inventory_receipt_gap"] = self.rng.randint(5, self.close_month)
        # параметры, нужные и месяцам, и посадке ошибок
        self.pay_per_25 = 25 * self.rng.randrange(3600, 4400, 40)   # делится на 25 нацело
        self.svc_monthly = self.rng.randrange(10000, 16000, 500)     # связь и охрана, константа
        self.ins_monthly = self.rng.randrange(8000, 14000, 500)      # страховка, константа
        self.rent = 45000
        self._accrual_outstanding = 0

    def build(self):
        y = self.year
        self._choose()
        self._je(f"{y}-01-01", self._t("je.founder"),
                 [("1000", 2500000, 0), ("3000", 0, 2500000)], "manual")
        self._je(f"{y}-01-05", self._t("je.opening_stock"),
                 [("1200", 300000, 0), ("1000", 0, 300000)], "manual", "STK-000")
        self._je(f"{y}-01-10", self._t("je.equipment"),
                 [("1500", 240000, 0), ("1000", 0, 240000)], "manual", "OS-001")
        self._je(f"{y}-01-02", self._t("je.insurance_policy"),
                 [("1300", self.ins_monthly * 12, 0), ("1000", 0, self.ins_monthly * 12)],
                 "manual", "INS-000")
        for m in range(1, self.close_month + 1):
            self._month(y, m)
        self._plant_errors()
        self._plant_decoys()
        self._plant_distractors()
        self._policy_document()
        self._finalize_bank_statement()
        return self

    # ---------- обычный месяц ----------
    def _gap(self, kind, m):
        """True, если в этом месяце операция данного вида пропущена (посаженная ошибка)."""
        return kind in self.chosen and self.gap_month[kind] == m

    def _month(self, y, m):
        last = eom(y, m).isoformat()
        is_close = (m == self.close_month)

        rev = 420000 + self.rng.randrange(-30000, 35000, 1000)
        self._je(f"{y}-{m:02d}-28", self._t("je.revenue", m=m),
                 [("1100", rev, 0), ("4000", 0, rev)], "ar", f"INV-{y}{m:02d}")
        cogs = int(rev * 0.42)

        # E17: поступление товара пропущено — запасы уходят в минус, ряд рвётся
        if not self._gap("inventory_receipt_gap", m):
            self._je(f"{y}-{m:02d}-26", self._t("je.goods_received", m=m),
                     [("1200", cogs, 0), ("2000", 0, cogs)], "ap", f"STK-{y}{m:02d}")
            paid = cogs
        else:
            paid = 0
            self._ir_gap_amount = cogs
        self._je(f"{y}-{m:02d}-28", self._t("je.cogs", m=m),
                 [("5000", cogs, 0), ("1200", 0, cogs)], "manual")
        self._je(f"{y}-{m:02d}-27", self._t("je.customer_receipts", m=m),
                 [("1000", int(rev * 0.9), 0), ("1100", 0, int(rev * 0.9))], "bank")
        if paid:
            self._je(f"{y}-{m:02d}-27", self._t("je.supplier_payment", m=m),
                     [("2000", paid, 0), ("1000", 0, paid)], "bank")
        self._je(f"{y}-{m:02d}-05", self._t("je.rent", m=m),
                 [("6100", self.rent, 0), ("1000", 0, self.rent)], "ap", f"RENT-{m:02d}")

        # зарплата: выплата 25-го за 1–25, остаток месяца — резерв (см. учётную политику)
        daily = self.pay_per_25 // 25
        outstanding = getattr(self, "_accrual_outstanding", 0)
        # E16: резерв прошлого месяца не погашен при выплате — вся сумма ушла в расход
        release = 0 if self._gap("accrual_not_released", m) else outstanding
        if self._gap("accrual_not_released", m):
            self._ar_gap_amount = outstanding
            pairs = [("6000", self.pay_per_25 + outstanding, 0),
                     ("1000", 0, self.pay_per_25 + outstanding)]
            outstanding = 0          # зависло на 2200 навсегда, повторно не гасится
        else:
            pairs = [("6000", self.pay_per_25, 0)]
            if release:
                pairs.append(("2200", release, 0))
            pairs.append(("1000", 0, self.pay_per_25 + release))
        self._je(f"{y}-{m:02d}-25", self._t("je.payroll", m=m), pairs, "payroll", f"PR-{m:02d}")
        self._accrual_outstanding = outstanding - release

        accrue = daily * (dim(y, m) - 25)
        # E13: резерв за хвост месяца не начислен
        if not self._gap("payroll_cutoff", m):
            self._je(last, self._t("je.payroll_accrual", m=m),
                     [("6000", accrue, 0), ("2200", 0, accrue)], "accrual", f"PRA-{m:02d}")
            self._accrual_outstanding += accrue
        else:
            self._pc_gap_amount = accrue

        util = 7000 + self.rng.randrange(-900, 2600, 100)
        self._je(last, self._t("je.electricity", m=m),
                 [("6200", util, 0), ("2000", 0, util)], "ap", f"UTIL-{y}{m:02d}")
        self._doc(f"UTIL-{y}{m:02d}", "vendor_invoice", last,
                  self._t("doc.util.title", m=m),
                  self._t("doc.util.body", m=m, kwh=util // 7, util=util),
                  {"vendor": self._t("vendor.util"), "amount": f"{util}.00"})

        # E9: регулярное начисление «связь и охрана» пропущено
        if not self._gap("missing_recurring", m):
            self._je(last, self._t("je.telecom", m=m),
                     [("6600", self.svc_monthly, 0), ("2100", 0, self.svc_monthly)],
                     "accrual", f"SEC-{m:02d}")

        # E15: ежемесячное списание годовой страховки пропущено
        if not self._gap("prepaid_amort_stopped", m):
            self._je(last, self._t("je.insurance_amort", m=m),
                     [("6800", self.ins_monthly, 0), ("1300", 0, self.ins_monthly)],
                     "accrual", f"INS-{m:02d}")

        # E14: амортизация пропущена
        if not self._gap("depreciation_stopped", m):
            self._je(last, self._t("je.depreciation", m=m),
                     [("6400", 4000, 0), ("1590", 0, 4000)], "accrual", f"DEP-{m:02d}")

    # ---------- посадка ----------
    def _plant_errors(self):
        planters = {
            "unrecorded_invoice": self._e_unrecorded_invoice,
            "duplicate_invoice": self._e_duplicate_invoice,
            "capex_expensed": self._e_capex_expensed,
            "prepaid_not_deferred": self._e_prepaid,
            "revenue_cutoff": self._e_revenue_cutoff,
            "unrecorded_bank_fee": self._e_bank_fee,
            "misclassified_expense": self._e_misclassified,
            "intercompany_mismatch": self._e_intercompany,
            "missing_recurring": self._e_missing_recurring,
            "fx_revaluation": self._e_fx,
            "depreciation_prorata": self._e_dep_prorata,
            "service_span_cutoff": self._e_span,
            "payroll_cutoff": self._e_payroll_cutoff,
            "depreciation_stopped": self._e_dep_stopped,
            "prepaid_amort_stopped": self._e_prepaid_amort,
            "accrual_not_released": self._e_accrual_not_released,
            "inventory_receipt_gap": self._e_inventory_gap,
        }
        for i, kind in enumerate(self.ERROR_KINDS):
            if kind in self.chosen:
                planters[kind](f"E{i+1}")

    def _err(self, eid, kind, desc, entry_ids, accounts, amount, dr, cr, ftype="require_entry"):
        self.errors.append(PlantedError(
            eid, kind, desc, entry_ids, accounts, f"{amount}",
            {"type": ftype, "period": [self.period_start, self.period_end],
             "debit_account": dr, "credit_account": cr, "amount": f"{amount}"}))

    # --- E1 ---
    def _e_unrecorded_invoice(self, eid):
        y, m = self.year, self.close_month
        amt = self.rng.randrange(40000, 90000, 1000)
        self._doc(f"SUB-{y}{m:02d}-1", "vendor_invoice", f"{y}-{m:02d}-27",
                  self._t("doc.sub.title"),
                  self._t("doc.sub.body", m=m, amt=amt, date=f"{y}-{m:02d}-27"),
                  {"vendor": self._t("vendor.torium"), "amount": f"{amt}.00"})
        self._err(eid, "unrecorded_invoice",
                  self._t("err.unrecorded_invoice", amt=amt),
                  [], ["5000", "2000"], f"{amt}.00", "5000", "2000")

    # --- E2 ---
    def _e_duplicate_invoice(self, eid):
        y, m = self.year, self.close_month
        dup = self.rng.randrange(15000, 45000, 500)
        ref2 = "AUD-114" if self.difficulty != "hard" else "AUD-114-R"
        e1 = self._je(f"{y}-{m:02d}-12", self._memo(self._t("memo.aud.plain"), self._t("memo.aud.terse")),
                      [("6300", dup, 0), ("2000", 0, dup)], "ap", "AUD-114")
        e2 = self._je(f"{y}-{m:02d}-19", self._memo(self._t("memo.aud.plain"), self._t("memo.aud.terse2")),
                      [("6300", dup, 0), ("2000", 0, dup)], "ap", ref2)
        self._doc("AUD-114", "vendor_invoice", f"{y}-{m:02d}-10",
                  self._t("doc.aud.title"),
                  self._t("doc.aud.body", amt=dup),
                  {"vendor": self._t("vendor.audit"), "amount": f"{dup}.00"})
        self._err(eid, "duplicate_invoice",
                  self._t("err.duplicate_invoice", e1=e1, e2=e2, amt=dup),
                  [e1, e2], ["6300", "2000"], f"{dup}.00", "2000", "6300", "require_reversal")

    # --- E3 ---
    def _e_capex_expensed(self, eid):
        y, m = self.year, self.close_month
        capex = self.rng.randrange(80000, 260000, 5000)
        e = self._je(f"{y}-{m:02d}-08", self._memo(self._t("memo.hw.plain"), self._t("memo.hw.terse")),
                     [("6900", capex, 0), ("1000", 0, capex)], "ap", "HW-7781")
        self._doc("HW-7781", "vendor_invoice", f"{y}-{m:02d}-08",
                  self._t("doc.hw.title"),
                  self._t("doc.hw.body", amt=capex),
                  {"vendor": self._t("vendor.hw"), "amount": f"{capex}.00"})
        self._err(eid, "capex_expensed",
                  self._t("err.capex_expensed", amt=capex),
                  [e], ["6900", "1500"], f"{capex}.00", "1500", "6900")

    # --- E4 ---
    def _e_prepaid(self, eid):
        y, m = self.year, self.close_month
        prepaid = self.rng.randrange(60000, 180000, 12000)
        e = self._je(f"{y}-{m:02d}-03", self._memo(self._t("memo.sw.plain"), self._t("memo.sw.terse")),
                     [("6500", prepaid, 0), ("1000", 0, prepaid)], "ap", "SW-900")
        self._doc("SW-900", "contract", f"{y}-{m:02d}-03",
                  self._t("doc.sw.title"),
                  self._t("doc.sw.body", date=f"{y}-{m:02d}-01", amt=prepaid),
                  {"vendor": self._t("vendor.sw"), "amount": f"{prepaid}.00"})
        self._err(eid, "prepaid_not_deferred",
                  self._t("err.prepaid_not_deferred", amt=prepaid, monthly=prepaid // 12),
                  [e], ["6500", "1300"], f"{prepaid - prepaid//12}.00", "1300", "6500")

    # --- E5 ---
    def _e_revenue_cutoff(self, eid):
        y, m = self.year, self.close_month
        adv = self.rng.randrange(50000, 140000, 5000)
        e = self._je(f"{y}-{m:02d}-20", self._memo(self._t("memo.adv.plain"), self._t("memo.adv.terse")),
                     [("1000", adv, 0), ("4000", 0, adv)], "ar", "ADV-51")
        self._doc("ADV-51", "contract", f"{y}-{m:02d}-20",
                  self._t("doc.adv.title"),
                  self._t("doc.adv.body", amt=adv, y1=y + 1),
                  {"customer": self._t("customer.vector"), "amount": f"{adv}.00"})
        self._err(eid, "revenue_cutoff",
                  self._t("err.revenue_cutoff", amt=adv),
                  [e], ["4000", "2400"], f"{adv}.00", "4000", "2400")

    # --- E6 ---
    def _e_bank_fee(self, eid):
        fee = self.rng.randrange(1500, 9000, 50)
        self._pending_bank_fee = fee
        self._err(eid, "unrecorded_bank_fee",
                  self._t("err.unrecorded_bank_fee", amt=fee),
                  [], ["6900", "1000"], f"{fee}.00", "6900", "1000")

    # --- E7 ---
    def _e_misclassified(self, eid):
        y, m = self.year, self.close_month
        amt = self.rng.randrange(20000, 60000, 1000)
        e = self._je(f"{y}-{m:02d}-15", self._memo(self._t("memo.ar.plain"), self._t("memo.ar.terse")),
                     [("6300", amt, 0), ("1000", 0, amt)], "ap", "AR-77")
        self._doc("AR-77", "contract", f"{y}-{m:02d}-15",
                  self._t("doc.ar.title"),
                  self._t("doc.ar.body", m=m, amt=amt),
                  {"vendor": self._t("vendor.ar"), "amount": f"{amt}.00"})
        self._err(eid, "misclassified_expense",
                  self._t("err.misclassified_expense", amt=amt),
                  [e], ["6300", "6100"], f"{amt}.00", "6100", "6300")

    # --- E8 ---
    def _e_intercompany(self, eid):
        y, m = self.year, self.close_month
        amt = self.rng.randrange(30000, 95000, 1000)
        self._doc(f"IC-{y}{m:02d}", "email", f"{y}-{m:02d}-29",
                  self._t("doc.ic.title"),
                  self._t("doc.ic.body", m=m, amt=amt, ic=f"IC-{y}{m:02d}"),
                  {"counterparty": self._t("counterparty.subsidiary"), "amount": f"{amt}.00"})
        self._err(eid, "intercompany_mismatch",
                  self._t("err.intercompany_mismatch", amt=amt),
                  [], ["6900", "2500"], f"{amt}.00", "6900", "2500")

    # --- E9: бездокументная. Ловится только разрывом в ряду начислений ---
    def _e_missing_recurring(self, eid):
        amt, gm = self.svc_monthly, self.gap_month["missing_recurring"]
        self._err(eid, "missing_recurring",
                  self._t("err.missing_recurring", amt=amt, m=gm),
                  [], ["6600", "2100"], f"{amt}.00", "6600", "2100")

    # --- E14: амортизация пропущена в одном месяце года ---
    def _e_dep_stopped(self, eid):
        gm = self.gap_month["depreciation_stopped"]
        self._err(eid, "depreciation_stopped",
                  self._t("err.depreciation_stopped", m=gm),
                  [], ["6400", "1590"], "4000.00", "6400", "1590")

    # --- E15: списание страховки пропущено в одном месяце года ---
    def _e_prepaid_amort(self, eid):
        amt, gm = self.ins_monthly, self.gap_month["prepaid_amort_stopped"]
        self._err(eid, "prepaid_amort_stopped",
                  self._t("err.prepaid_amort_stopped", amt=amt, m=gm),
                  [], ["6800", "1300"], f"{amt}.00", "6800", "1300")

    # --- E16: резерв прошлого месяца не погашен при выплате ---
    def _e_accrual_not_released(self, eid):
        amt, gm = self._ar_gap_amount, self.gap_month["accrual_not_released"]
        self._err(eid, "accrual_not_released",
                  self._t("err.accrual_not_released", amt=amt, m=gm),
                  [], ["2200", "6000"], f"{amt}.00", "2200", "6000")

    # --- E17: поступление товара пропущено в одном месяце года ---
    def _e_inventory_gap(self, eid):
        amt, gm = self._ir_gap_amount, self.gap_month["inventory_receipt_gap"]
        self._err(eid, "inventory_receipt_gap",
                  self._t("err.inventory_receipt_gap", amt=amt, m=gm),
                  [], ["1200", "2000"], f"{amt}.00", "1200", "2000")

    # --- E10: расчётная. Переоценка валютной кредиторки ---
    def _e_fx(self, eid):
        y, m = self.year, self.close_month
        eur = self.rng.randrange(800, 2600, 100)
        r1 = D(f"{95 + self.rng.randrange(0, 500) / 100:.2f}")
        delta = D(f"{self.rng.randrange(150, 450) / 100:.2f}")
        r2 = r1 + delta
        base = D(eur) * r1
        e = self._je(f"{y}-{m:02d}-14", self._memo(self._t("memo.nw.plain"), self._t("memo.nw.terse")),
                     [("5000", base, 0), ("2000", 0, base)], "ap", "NW-2210")
        self._doc("NW-2210", "vendor_invoice", f"{y}-{m:02d}-14",
                  self._t("doc.nw.title"),
                  self._t("doc.nw.body", eur=eur, date=f"{y}-{m:02d}-14", r1=r1),
                  {"vendor": self._t("vendor.nw"), "currency": "EUR", "amount_eur": f"{eur}.00"})
        self._doc(f"FX-{y}{m:02d}", "policy", self.period_end,
                  self._t("doc.fx.title"),
                  self._t("doc.fx.body", date=f"{y}-{m:02d}-14", r1=r1, end=self.period_end, r2=r2),
                  {})
        self._err(eid, "fx_revaluation",
                  self._t("err.fx_revaluation", eur=eur, r1=r1, r2=r2, diff=D(eur) * delta),
                  [e], ["6700", "2000"], f"{D(eur) * delta}", "6700", "2000")

    # --- E11: расчётная. Амортизация нового ОС по дням ---
    def _e_dep_prorata(self, eid):
        y, m = self.year, self.close_month
        cost = 90 * self.rng.randrange(2000, 4000, 100)   # делится на 90 нацело
        days = dim(y, m) - 11 + 1
        amount = D(cost) * D(days) / D(dim(y, m)) / D(60)
        e = self._je(f"{y}-{m:02d}-11", self._memo(self._t("memo.ml.plain"), self._t("memo.ml.terse")),
                     [("1500", cost, 0), ("1000", 0, cost)], "manual", "ML-330")
        self._doc("ML-330", "vendor_invoice", f"{y}-{m:02d}-11",
                  self._t("doc.ml.title"),
                  self._t("doc.ml.body", amt=cost, date=f"{y}-{m:02d}-11"),
                  {"vendor": self._t("vendor.ml"), "amount": f"{cost}.00"})
        self._err(eid, "depreciation_prorata",
                  self._t("err.depreciation_prorata", amt=cost, date=f"{y}-{m:02d}-11",
                          days=days, dep=amount),
                  [e], ["6400", "1590"], f"{amount}", "6400", "1590")

    # --- E12: расчётная. Услуга через границу периода ---
    def _e_span(self, eid):
        y, m = self.year, self.close_month
        total = 4 * self.rng.randrange(30000, 80000, 1000)   # делится на 4 нацело
        start = dt.date(y, m, 16)
        end = start + dt.timedelta(days=59)                  # ровно 60 дней
        in_period = (eom(y, m) - start).days + 1             # 15 дней в ноябре
        defer = D(total) * D(60 - in_period) / D(60)
        e = self._je(f"{y}-{m:02d}-16", self._memo(self._t("memo.qb.plain"), self._t("memo.qb.terse")),
                     [("6300", total, 0), ("1000", 0, total)], "ap", "QB-88")
        self._doc("QB-88", "contract", f"{y}-{m:02d}-16",
                  self._t("doc.qb.title"),
                  self._t("doc.qb.body", start=start.isoformat(), end=end.isoformat(), amt=total),
                  {"vendor": self._t("vendor.qb"), "amount": f"{total}.00"})
        self._err(eid, "service_span_cutoff",
                  self._t("err.service_span_cutoff", amt=total, in_period=in_period, defer=defer),
                  [e], ["1300", "6300"], f"{defer}", "1300", "6300")

    # --- E13: расчётная и бездокументная. Резерв по зарплате ---
    def _e_payroll_cutoff(self, eid):
        gm = self.gap_month["payroll_cutoff"]
        amt = self._pc_gap_amount
        tail = dim(self.year, gm) - 25
        self._err(eid, "payroll_cutoff",
                  self._t("err.payroll_cutoff", tail=tail, amt=amt, m=gm),
                  [], ["6000", "2200"], f"{amt}.00", "6000", "2200")

    # ---------- двойники-пустышки ----------
    def _plant_decoys(self):
        """Для каждого НЕ посаженного типа — похожий, но законный след.
        Иначе состав задачи читается по инвентарю документов."""
        y, m, last = self.year, self.close_month, self.period_end

        if "unrecorded_invoice" not in self.chosen:
            amt = self.rng.randrange(40000, 90000, 1000)
            self._je(f"{y}-{m:02d}-27", self._t("je.sub_decoy"),
                     [("5000", amt, 0), ("2000", 0, amt)], "ap", f"SUB-{y}{m:02d}-1")
            self._doc(f"SUB-{y}{m:02d}-1", "vendor_invoice", f"{y}-{m:02d}-27",
                      self._t("doc.sub.title"),
                      self._t("doc.sub.body_decoy", m=m, amt=amt),
                      {"vendor": self._t("vendor.torium"), "amount": f"{amt}.00"})

        if "duplicate_invoice" not in self.chosen:
            amt = self.rng.randrange(15000, 45000, 500)
            self._je(f"{y}-{m:02d}-12", self._t("memo.aud.terse"),
                     [("6300", amt, 0), ("2000", 0, amt)], "ap", "AUD-114")
            self._doc("AUD-114", "vendor_invoice", f"{y}-{m:02d}-10",
                      self._t("doc.aud.title"),
                      self._t("doc.aud.body", amt=amt),
                      {"vendor": self._t("vendor.audit"), "amount": f"{amt}.00"})

        if "capex_expensed" not in self.chosen:
            amt = self.rng.randrange(80000, 260000, 5000)
            self._je(f"{y}-{m:02d}-08", self._t("memo.hw.terse"),
                     [("1500", amt, 0), ("1000", 0, amt)], "manual", "HW-7781")
            self._doc("HW-7781", "vendor_invoice", f"{y}-{m:02d}-08",
                      self._t("doc.hw.title"),
                      self._t("doc.hw.body_decoy", amt=amt),
                      {"vendor": self._t("vendor.hw"), "amount": f"{amt}.00"})

        if "prepaid_not_deferred" not in self.chosen:
            amt = self.rng.randrange(8000, 20000, 1000)
            self._je(f"{y}-{m:02d}-03", self._t("memo.sw.terse"),
                     [("6500", amt, 0), ("1000", 0, amt)], "ap", "SW-900")
            self._doc("SW-900", "contract", f"{y}-{m:02d}-03",
                      self._t("doc.sw.title"),
                      self._t("doc.sw.body_decoy", m=m, amt=amt),
                      {"vendor": self._t("vendor.sw"), "amount": f"{amt}.00"})

        if "revenue_cutoff" not in self.chosen:
            amt = self.rng.randrange(50000, 140000, 5000)
            self._je(f"{y}-{m:02d}-20", self._t("memo.adv.terse"),
                     [("1000", amt, 0), ("1100", 0, amt)], "ar", "ADV-51")
            self._doc("ADV-51", "contract", f"{y}-{m:02d}-20",
                      self._t("doc.adv.title"),
                      self._t("doc.adv.body_decoy", m=m, amt=amt, date=f"{y}-{m:02d}-18"),
                      {"customer": self._t("customer.vector"), "amount": f"{amt}.00"})

        if "misclassified_expense" not in self.chosen:
            amt = self.rng.randrange(20000, 60000, 1000)
            self._je(f"{y}-{m:02d}-15", self._t("memo.ar.terse"),
                     [("6100", amt, 0), ("1000", 0, amt)], "ap", "AR-77")
            self._doc("AR-77", "contract", f"{y}-{m:02d}-15",
                      self._t("doc.ar.title"),
                      self._t("doc.ar.body_decoy", m=m, amt=amt),
                      {"vendor": self._t("vendor.ar"), "amount": f"{amt}.00"})

        if "intercompany_mismatch" not in self.chosen:
            self._doc(f"IC-{y}{m:02d}", "email", f"{y}-{m:02d}-29",
                      self._t("doc.ic.title"),
                      self._t("doc.ic.body_decoy", m=m), {})

        if "fx_revaluation" not in self.chosen:
            eur = self.rng.randrange(800, 2600, 100)
            r1 = D(f"{95 + self.rng.randrange(0, 500) / 100:.2f}")
            base = D(eur) * r1
            e = self._je(f"{y}-{m:02d}-14", self._t("memo.nw.terse"),
                         [("5000", base, 0), ("2000", 0, base)], "ap", "NW-2210")
            self._je(f"{y}-{m:02d}-24", self._t("je.nw_settle"),
                     [("2000", base, 0), ("1000", 0, base)], "bank", "NW-2210")
            self._doc("NW-2210", "vendor_invoice", f"{y}-{m:02d}-14",
                      self._t("doc.nw.title"),
                      self._t("doc.nw.body_decoy", eur=eur, r1=r1, date=f"{y}-{m:02d}-24"),
                      {"vendor": self._t("vendor.nw"), "currency": "EUR", "amount_eur": f"{eur}.00"})
            self._doc(f"FX-{y}{m:02d}", "policy", self.period_end,
                      self._t("doc.fx.title"),
                      self._t("doc.fx.body_decoy", date=f"{y}-{m:02d}-14", r1=r1, end=self.period_end), {})

        if "depreciation_prorata" not in self.chosen:
            cost = 90 * self.rng.randrange(2000, 4000, 100)
            days = dim(y, m) - 11 + 1
            amount = D(cost) * D(days) / D(dim(y, m)) / D(60)
            self._je(f"{y}-{m:02d}-11", self._t("memo.ml.terse"),
                     [("1500", cost, 0), ("1000", 0, cost)], "manual", "ML-330")
            self._je(last, self._t("je.ml_dep_decoy", days=days),
                     [("6400", amount, 0), ("1590", 0, amount)], "accrual", "ML-330")
            self._doc("ML-330", "vendor_invoice", f"{y}-{m:02d}-11",
                      self._t("doc.ml.title"),
                      self._t("doc.ml.body", amt=cost, date=f"{y}-{m:02d}-11"),
                      {"vendor": self._t("vendor.ml"), "amount": f"{cost}.00"})

        if "service_span_cutoff" not in self.chosen:
            total = 4 * self.rng.randrange(30000, 80000, 1000)
            start = dt.date(y, m, 5)
            end = dt.date(y, m, 25)
            self._je(f"{y}-{m:02d}-16", self._t("memo.qb.terse"),
                     [("6300", total, 0), ("1000", 0, total)], "ap", "QB-88")
            self._doc("QB-88", "contract", f"{y}-{m:02d}-16",
                      self._t("doc.qb.title"),
                      self._t("doc.qb.body_decoy", start=start.isoformat(), end=end.isoformat(), amt=total),
                      {"vendor": self._t("vendor.qb"), "amount": f"{total}.00"})

    # ---------- законные ловушки ----------
    def _plant_distractors(self):
        """Законные операции, похожие на ошибки. Исправлять их НЕ нужно — за это штраф."""
        if self.difficulty != "hard":
            return
        y, m = self.year, self.close_month
        a1 = self.rng.randrange(9000, 18000, 500)
        self._je(f"{y}-{m:02d}-07", self._t("je.cs", n="CS-401"),
                 [("6900", a1, 0), ("2000", 0, a1)], "ap", "CS-401")
        self._je(f"{y}-{m:02d}-21", self._t("je.cs", n="CS-402"),
                 [("6900", a1, 0), ("2000", 0, a1)], "ap", "CS-402")
        for n, per in (("CS-401", "half.first"), ("CS-402", "half.second")):
            self._doc(n, "vendor_invoice", f"{y}-{m:02d}-07",
                      self._t("doc.cs.title", n=n),
                      self._t("doc.cs.body", per=self._t(per), m=m, amt=a1),
                      {"vendor": self._t("vendor.cs"), "amount": f"{a1}.00"})
        a2 = self.rng.randrange(60000, 110000, 5000)
        self._je(f"{y}-{m:02d}-11", self._t("je.pt"),
                 [("6900", a2, 0), ("1000", 0, a2)], "ap", "PT-55")
        self._doc("PT-55", "vendor_invoice", f"{y}-{m:02d}-11",
                  self._t("doc.pt.title"),
                  self._t("doc.pt.body", amt=a2),
                  {"vendor": self._t("vendor.pt"), "amount": f"{a2}.00"})

    # ---------- учётная политика ----------
    def _policy_document(self):
        tail = dim(self.year, self.close_month) - 25
        self._doc("POL-01", "policy", f"{self.year}-01-01",
                  self._t("doc.pol.title"),
                  self._t("doc.pol.body", m=self.close_month, tail=tail), {})

    def _finalize_bank_statement(self):
        """Выписка считается последней: остаток сходится с книгой минус комиссия."""
        y, m, last = self.year, self.close_month, self.period_end
        fee = getattr(self, "_pending_bank_fee", None)
        bal = self.ledger.balance("1000", last) - D(fee or 0)
        if fee is None:
            body = self._t("doc.bank.body_nofee", bal=bal)
        else:
            body = self._t("doc.bank.body_fee", bal=bal, fee=fee, date=last)
        self._doc(f"BANK-{y}{m:02d}", "bank_statement", last,
                  self._t("doc.bank.title", m=m), body, {})

    # ---------- сериализация ----------
    def snapshot(self) -> dict:
        return {
            "company": self.name, "seed": self.seed,
            "period": {"start": self.period_start, "end": self.period_end},
            "accounts": [{"code": a.code, "name": a.name, "type": a.type} for a in self.coa],
            "entries": [{"eid": e.eid, "date": e.date, "memo": e.memo, "source": e.source, "ref": e.ref,
                         "lines": [{"account": l.account, "debit": str(l.debit), "credit": str(l.credit)}
                                   for l in e.lines]} for e in self.ledger.entries],
            "documents": [asdict(d) for d in self.documents],
        }

    def truth(self) -> dict:
        return {"errors": [asdict(e) for e in self.errors]}
