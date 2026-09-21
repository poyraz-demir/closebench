# closebench

[![tests](https://github.com/poyraz-demir/closebench/actions/workflows/tests.yml/badge.svg)](https://github.com/poyraz-demir/closebench/actions/workflows/tests.yml)

Deterministic, seeded double-entry ledgers with planted month-end closing errors and a
programmatic grader. Zero dependencies. Built for testing bookkeeping agents.

```python
from closebench.world import World
from closebench.tools import Session
from closebench.grader import grade

world = World(seed=7).build()        # same seed → byte-identical books, every time
agent = Session(world)               # the only surface an agent ever sees

print(agent.trial_balance())         # ...agent reads the books, documents, policy...
agent.post_entry("2026-11-30", "capitalise HW-7781", [
    {"account": "1500", "debit": "175000.00"},
    {"account": "6900", "credit": "175000.00"},
])

print(grade(world, agent))
# {'passed': False, 'score': 0.143, 'found': ['E3'], 'partial': [], 'missed': [...],
#  'spurious_entries': [], 'tb_balanced': True, ...}
```

## Why this exists

If you are building an agent that closes the books, you need books to close — with
errors you planted yourself, so you know the answer. Real ERP exports are messy, slow,
legally encumbered and never reproducible. LLM-judged rubrics drift.

`closebench` gives you a company: eleven months of operations, a chart of accounts,
supporting documents, an accounting policy, and a fixed set of closing errors chosen by
the seed. The grader checks the agent's adjusting entries against the planted errors by
account and amount — no rubric, no judge model, no human in the loop.

Use it as a regression suite: run your agent over 50 seeds on every change and watch
`pass_rate` and `mean_score`.

## What a world contains

| | |
|---|---|
| Ledger | ~140 balanced entries across 11 months, 26-account chart, cash and inventory never negative |
| Documents | ~25: vendor invoices, contracts, bank statement, intercompany email, FX rate certificate, accounting policy |
| Planted errors | 6–9 per world in `hard` mode, 4–6 in `absence` mode |
| Distractors | legitimate transactions that look like errors — correcting them costs points |
| Decoys | every error type has a legitimate twin, so the document inventory never reveals what was planted |
| Truth | `world.errors` — hidden from the agent, used by the grader |

Two locales: `lang="en"` (default) and `lang="ru"`. Numbers, dates, accounts and errors are
identical across locales; only text differs.

## Error taxonomy

**Document-backed** (the evidence is in a document the agent can read):

| kind | what went wrong | correct fix |
|---|---|---|
| `unrecorded_invoice` | subcontractor act never posted | Dr 5000 / Cr 2000 |
| `duplicate_invoice` | one invoice posted twice under two refs | Dr 2000 / Cr 6300 |
| `capex_expensed` | fixed asset above the policy limit expensed | Dr 1500 / Cr 6900 |
| `prepaid_not_deferred` | 12-month licence expensed in full | Dr 1300 / Cr 6500 |
| `revenue_cutoff` | customer prepayment for next year booked as revenue | Dr 4000 / Cr 2400 |
| `unrecorded_bank_fee` | fee on the bank statement, not in the books | Dr 6900 / Cr 1000 |
| `misclassified_expense` | warehouse rent booked to professional services | Dr 6100 / Cr 6300 |
| `intercompany_mismatch` | subsidiary's services never recorded | Dr 6900 / Cr 2500 |
| `fx_revaluation` | open EUR payable not revalued at period-end rate | Dr 6700 / Cr 2000 |
| `depreciation_prorata` | new asset in service mid-month, no depreciation (day-prorated) | Dr 6400 / Cr 1590 |
| `service_span_cutoff` | 60-day contract straddling period end, expensed in full (day-prorated) | Dr 1300 / Cr 6300 |

**Absence-only** (no document points at them — the error exists only as a gap in a series,
and it is hidden in a **random month of the year**, not the closing month):

| kind | what went wrong | correct fix |
|---|---|---|
| `missing_recurring` | one month's security-services accrual missing | Dr 6600 / Cr 2100 |
| `payroll_cutoff` | one month's end-of-month payroll accrual missing | Dr 6000 / Cr 2200 |
| `depreciation_stopped` | one month's depreciation missing | Dr 6400 / Cr 1590 |
| `prepaid_amort_stopped` | one month's insurance amortisation missing | Dr 6800 / Cr 1300 |
| `accrual_not_released` | prior-month accrual not released at payment; expense double-counted | Dr 2200 / Cr 6000 |
| `inventory_receipt_gap` | goods received never posted although COGS was | Dr 1200 / Cr 2000 |

`hard` mode samples 6–9 kinds from all seventeen. `absence` mode samples 4–6 from the six
absence-only kinds. Amounts are seeded so that no two planted errors in one world share
the same account pair and amount.

## Grading

```python
grade(world, session) -> {
  "passed": bool,          # every error found (exact or partial), TB balanced, nothing spurious
  "score": float,          # (exact + 0.5·partial) / total − 0.1·spurious, floored at 0
  "found": [...],          # exact account pair and amount
  "partial": [...],        # right amount, economically equivalent account (e.g. 6300 for 6900)
  "missed": [...],
  "spurious_entries": [...],   # adjustments matching no planted error
  "tb_balanced": bool,
  "adjustments_posted": int,
  "tool_calls": int,
}
```

An adjustment can satisfy at most one planted error. Equivalence groups are small and
explicit (`grader.EQUIV`); a defensible account choice earns half credit, never a penalty.

## Agent tools

`chart_of_accounts`, `trial_balance`, `journal`, `account_detail`, `list_documents`,
`read_document`, `pnl`, `post_entry`. Nothing else. The agent never sees `world.errors`.

## Command line

The CLI keeps truth in process memory only: the world is rebuilt from the seed on every
call and just the agent's postings are persisted, so an agent driving the CLI cannot read
the answer key from disk.

```bash
closebench --session demo --start 7 --lang en
closebench --session demo --tool trial_balance
closebench --session demo --tool read_document --args '{"doc_id": "POL-01"}'
closebench --session demo --tool post_entry --args '{"date":"2026-11-30","memo":"...","lines":[...]}'
closebench --session demo --finish        # grades and seals the session
```

Seeds ≥ 1000 select `absence` mode. Sessions are sealed after `--finish`.
Session state lives in `./closebench_runs/` (override with `CLOSEBENCH_RUNS`).

## Running a model

`closebench.runner` contains a minimal tool-calling loop with Anthropic and OpenAI
backends (API key from the environment). It is deliberately small; wire in your own agent.

```bash
python -m closebench.runner --seeds 1,2,3,4,5 --backend anthropic --model claude-sonnet-5
```

## What to expect

This is a **regression suite, not a hard benchmark.** In our runs a frontier model with a
neutral prompt closed `hard` worlds with 83 % pass rate and `absence` worlds with 58 %
(92 % if you accept the agent's refusal to book an undocumented goods receipt). Distractors
caught nobody. Use the score to catch regressions in your own agent, not to rank models.

The one thing models still get wrong: two errors that cancel in the balances (e.g. a
missing accrual and an unreleased accrual of the same amount). They are still two errors.

## Install

```bash
pip install closebench
```

Python ≥ 3.10, no dependencies. Tests: `pip install pytest && python -m pytest -q`.

## Licence

MIT.
