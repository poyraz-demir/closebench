"""Запуск агента в среде. Бэкенд модели подключаемый; ключи берутся из окружения."""
from __future__ import annotations
import json, os, re, sys
from closebench.world import World
from closebench.tools import Session, tool_spec
from closebench.grader import grade
from closebench.strings import T, LANGS

CALL_RE = re.compile(r'^CALL\s+(\w+)\s*(\{.*\})?\s*$', re.M)

def system_prompt(lang: str, start: str, end: str) -> str:
    tools_txt = "\n".join(T(lang, "cli.tool_line", **t) for t in tool_spec(lang))
    return T(lang, "runner.system", start=start, end=end, tools=tools_txt)

def dispatch(sess: Session, name: str, args: dict) -> str:
    fn = getattr(sess, name, None)
    if not fn or name.startswith("_"):
        return T(sess.lang, "runner.no_tool", name=name)
    try:
        return fn(**args)
    except TypeError as e:
        return T(sess.lang, "runner.bad_params", name=name, e=e)

def run_episode(seed: int, backend, max_turns: int = 30, verbose=False, lang: str = "en") -> dict:
    from closebench.cli import mode_for
    w = World(seed=seed, lang=lang, difficulty=mode_for(seed)).build()
    s = Session(w)
    sys_prompt = system_prompt(lang, w.period_start, w.period_end)
    # Слово-стоп ищется как целое слово: «DONE» иначе ловился бы внутри «undone».
    done_re = re.compile(r"\b" + re.escape(T(lang, "runner.done")) + r"\b")
    msgs = [{"role": "user", "content": T(lang, "runner.begin")}]
    transcript = []
    for turn in range(max_turns):
        reply = backend(sys_prompt, msgs)
        transcript.append({"role": "assistant", "text": reply})
        if verbose: print(f"{T(lang, 'runner.turn', n=turn+1)}\n{reply[:900]}\n")
        calls = CALL_RE.findall(reply)
        if not calls:
            break
        results = []
        for name, raw in calls:
            try:
                args = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                results.append(T(lang, "runner.bad_json", name=name)); continue
            results.append(f"[{name}]\n{dispatch(s, name, args)}")
        obs = "\n\n".join(results)
        msgs.append({"role": "assistant", "content": reply})
        msgs.append({"role": "user", "content": T(lang, "runner.results", obs=obs)})
        transcript.append({"role": "tool", "text": obs})
        if done_re.search(reply.upper()):
            break
    res = grade(w, s)
    res["seed"] = seed
    res["turns"] = turn + 1
    return {"grade": res, "transcript": transcript, "tool_log": s.calls}

# ---------- бэкенды ----------
def anthropic_backend(model="claude-sonnet-5"):
    import urllib.request
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key: raise RuntimeError("ANTHROPIC_API_KEY is not set")
    def call(system, msgs):
        body = json.dumps({"model": model, "max_tokens": 2000, "system": system,
                           "messages": msgs}).encode()
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body,
            headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.load(r)
        return "".join(b.get("text", "") for b in d.get("content", []))
    return call

def openai_backend(model="gpt-5"):
    import urllib.request
    key = os.environ.get("OPENAI_API_KEY")
    if not key: raise RuntimeError("OPENAI_API_KEY is not set")
    def call(system, msgs):
        body = json.dumps({"model": model, "messages": [{"role": "system", "content": system}] + msgs}).encode()
        req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=body,
            headers={"authorization": f"Bearer {key}", "content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.load(r)
        return d["choices"][0]["message"]["content"]
    return call

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="1,2,3,4,5,6,7,8,9,10")
    ap.add_argument("--backend", default="anthropic")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--lang", choices=LANGS, default="en")
    ap.add_argument("--out", default="runs/result.json")
    a = ap.parse_args()
    be = {"anthropic": anthropic_backend, "openai": openai_backend}[a.backend](a.model)
    results = []
    for sd in [int(x) for x in a.seeds.split(",")]:
        r = run_episode(sd, be, lang=a.lang)
        results.append(r["grade"])
        print(json.dumps(r["grade"], ensure_ascii=False))
    passed = sum(1 for r in results if r["passed"])
    summary = {"model": a.model, "lang": a.lang, "n": len(results), "pass_rate": passed / len(results),
               "mean_score": round(sum(r["score"] for r in results) / len(results), 3),
               "results": results}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(summary, open(a.out, "w"), ensure_ascii=False, indent=2)
    print(T(a.lang, "runner.summary"),
          json.dumps({k: summary[k] for k in ("model", "lang", "n", "pass_rate", "mean_score")}, ensure_ascii=False))
