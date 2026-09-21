"""Интерфейс агента: состояние сессии на диске, истина только в памяти процесса.
Агент вызывает инструменты и не имеет доступа к посаженным ошибкам."""
from __future__ import annotations
import argparse, json, os, sys
from closebench.world import World
from closebench.tools import Session, tool_spec
from closebench.grader import grade
from closebench.strings import T, LANGS

RUNS = os.environ.get("CLOSEBENCH_RUNS", os.path.join(os.getcwd(), "closebench_runs"))

def state_path(sid): return os.path.join(RUNS, f"session_{sid}.json")

def mode_for(seed: int) -> str:
    """Режим кодируется номером сида, а не флагом: флаг виден агенту в командной
    строке и сам по себе является подсказкой о характере задачи."""
    return "absence" if seed >= 1000 else "hard"

def load(sid):
    p = state_path(sid)
    if not os.path.exists(p): return None
    return json.load(open(p))

def save(sid, st):
    os.makedirs(RUNS, exist_ok=True)
    json.dump(st, open(state_path(sid), "w"), ensure_ascii=False)

def rebuild(sid):
    """Восстанавливаем мир по seed и переигрываем проводки агента."""
    st = load(sid)
    if not st: return None, None, None
    # Сессии, записанные до появления поля lang, были русскими.
    w = World(seed=st["seed"], lang=st.get("lang", "ru"),
              difficulty=st.get("mode", "hard")).build()
    s = Session(w)
    for a in st["posted"]:
        s.post_entry(a["date"], a["memo"], a["lines"])
    s.external_calls = st.get("calls", 0)
    return st, w, s

def tools_text(lang: str) -> str:
    return "\n".join(T(lang, "cli.tool_line", **t) for t in tool_spec(lang))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True)
    ap.add_argument("--start", type=int, help="seed of a new episode")
    ap.add_argument("--lang", choices=LANGS, default="en",
                    help="world language for --start (default: en); stored in the session")
    ap.add_argument("--tool")
    ap.add_argument("--args", default="{}")
    ap.add_argument("--finish", action="store_true")
    a = ap.parse_args()

    if a.start is not None:
        mode, lang = mode_for(a.start), a.lang
        w = World(seed=a.start, lang=lang, difficulty=mode).build()
        save(a.session, {"seed": a.start, "mode": mode, "lang": lang, "posted": [], "calls": 0})
        print(T(lang, "cli.started", start=w.period_start, end=w.period_end, name=w.name))
        print(T(lang, "cli.counts", entries=len(w.ledger.entries), documents=len(w.documents)))
        print(T(lang, "cli.task", end=w.period_end))
        print(T(lang, "cli.no_extra"))
        print(T(lang, "cli.tools", tools=tools_text(lang)))
        return

    st, w, s = rebuild(a.session)
    if not st:
        print(T(a.lang, "cli.session_not_found")); sys.exit(1)
    lang = w.lang

    if a.finish:
        res = grade(w, s)
        res["seed"] = st["seed"]
        st["closed"] = True
        save(a.session, st)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return

    if st.get("closed"):
        print(T(lang, "cli.closed")); sys.exit(1)

    try:
        args = json.loads(a.args)
    except json.JSONDecodeError as e:
        print(T(lang, "cli.bad_json", e=e)); sys.exit(1)

    fn = getattr(s, a.tool, None)
    if not fn or a.tool.startswith("_"):
        print(T(lang, "cli.no_tool", tool=a.tool)); sys.exit(1)
    before = len(s.posted)
    try:
        out = fn(**args)
    except TypeError as e:
        print(T(lang, "cli.bad_params", e=e)); sys.exit(1)

    # Успешная проводка распознаётся по факту, а не по тексту ответа (текст зависит от языка).
    if a.tool == "post_entry" and len(s.posted) > before:
        st["posted"].append({"date": args["date"], "memo": args["memo"], "lines": args["lines"]})
    st["calls"] += 1
    save(a.session, st)
    print(out)

if __name__ == "__main__":
    main()
