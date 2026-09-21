"""Инструменты агента. Агент видит ТОЛЬКО это — истина про ошибки ему недоступна."""
from __future__ import annotations
import json
from decimal import Decimal
from closebench.ledger import Entry, Line, D
from closebench.strings import T, LANGS

class Session:
    def __init__(self, world):
        self.w = world
        self.L = world.ledger
        self.lang = world.lang
        self.calls: list[dict] = []
        self.posted: list[str] = []

    def _t(self, key, **fmt):
        return T(self.lang, key, **fmt)

    def _log(self, name, args, result_summary):
        self.calls.append({"tool": name, "args": args, "result": result_summary})

    # --- чтение ---
    def chart_of_accounts(self) -> str:
        rows = [f"{c} | {a.name:<35} | {a.type}" for c, a in sorted(self.L.accounts.items())]
        self._log("chart_of_accounts", {}, self._t("tool.log.accounts", n=len(rows)))
        return self._t("tool.coa_header") + "\n" + "\n".join(rows)

    def trial_balance(self, upto: str | None = None) -> str:
        upto = upto or self.w.period_end
        rows = self.L.trial_balance(upto)
        out = [self._t("tool.tb_header")]
        for r in rows:
            out.append(f"{r['code']} | {r['name'][:33]:<33} | {str(r['debit']):>10} | {str(r['credit']):>10}")
        d, c = self.L.tb_totals(upto)
        status = self._t("tool.balanced" if d == c else "tool.unbalanced")
        out.append(self._t("tool.tb_total", d=d, c=c, status=status))
        self._log("trial_balance", {"upto": upto}, self._t("tool.log.rows", n=len(rows)))
        return "\n".join(out)

    def journal(self, start: str | None = None, end: str | None = None, account: str | None = None) -> str:
        start = start or self.w.period_start
        end = end or self.w.period_end
        dr, cr = self._t("tool.dr"), self._t("tool.cr")
        rows = []
        for e in self.L.in_period(start, end):
            if account and not any(l.account == account for l in e.lines):
                continue
            legs = " ; ".join(f"{l.account} {dr}{l.debit}" if l.debit else f"{l.account} {cr}{l.credit}"
                              for l in e.lines)
            rows.append(f"{e.eid} | {e.date} | {e.source:<8} | ref={e.ref or '-':<12} | {e.memo[:40]:<40} | {legs}")
        self._log("journal", {"start": start, "end": end, "account": account},
                  self._t("tool.log.entries", n=len(rows)))
        return "\n".join(rows) if rows else self._t("tool.empty")

    def account_detail(self, code: str, upto: str | None = None) -> str:
        upto = upto or self.w.period_end
        if code not in self.L.accounts:
            self._log("account_detail", {"code": code}, self._t("tool.log.no_account"))
            return self._t("tool.no_account", code=code)
        bal = self.L.balance(code, upto)
        acc = self.L.accounts[code]
        self._log("account_detail", {"code": code}, str(bal))
        return self._t("tool.balance", code=code, name=acc.name, type=acc.type, upto=upto, bal=bal)

    def list_documents(self, kind: str | None = None) -> str:
        docs = [d for d in self.w.documents if not kind or d.kind == kind]
        self._log("list_documents", {"kind": kind}, self._t("tool.log.documents", n=len(docs)))
        return "\n".join(f"{d.doc_id} | {d.date} | {d.kind:<16} | {d.title}" for d in docs) or self._t("tool.empty")

    def read_document(self, doc_id: str) -> str:
        for d in self.w.documents:
            if d.doc_id == doc_id:
                self._log("read_document", {"doc_id": doc_id}, "ok")
                meta = json.dumps(d.meta, ensure_ascii=False)
                return (f"=== {d.doc_id} ({d.kind}, {d.date}) ===\n{d.title}\n\n{d.body}\n\n"
                        f"{self._t('tool.meta')}: {meta}")
        self._log("read_document", {"doc_id": doc_id}, self._t("tool.log.not_found"))
        return self._t("tool.doc_not_found", doc_id=doc_id)

    def pnl(self, start: str | None = None, end: str | None = None) -> str:
        start, end = start or self.w.period_start, end or self.w.period_end
        p = self.L.pnl(start, end)
        self._log("pnl", {"start": start, "end": end}, str(p["net"]))
        return self._t("tool.pnl", start=start, end=end,
                       income=p["income"], expense=p["expense"], net=p["net"])

    # --- запись ---
    def post_entry(self, date: str, memo: str, lines: list[dict]) -> str:
        try:
            ls = [Line(l["account"], D(l.get("debit", 0)), D(l.get("credit", 0))) for l in lines]
            e = Entry(self.L.next_id("ADJ"), date, memo, ls, source="close_adj")
            self.L.post(e)
            self.posted.append(e.eid)
            self._log("post_entry", {"date": date, "memo": memo, "lines": lines}, e.eid)
            return self._t("tool.posted", eid=e.eid)
        except Exception as ex:
            self._log("post_entry", {"date": date, "memo": memo, "lines": lines},
                      self._t("tool.log.error", ex=ex))
            return self._t("tool.error", ex=ex)

_TOOL_NAMES = ["chart_of_accounts", "trial_balance", "journal", "account_detail",
               "list_documents", "read_document", "pnl", "post_entry"]

def tool_spec(lang: str = "en") -> list[dict]:
    """Описание инструментов на языке `lang` (имена инструментов не переводятся)."""
    return [{"name": n,
             "params": T(lang, f"spec.{n}.params"),
             "desc": T(lang, f"spec.{n}.desc")} for n in _TOOL_NAMES]

TOOL_SPEC = tool_spec("en")
