"""Набор задач: 10 вариантов мира с разными seed и составом ошибок.
Пишет в <outdir>/<lang>/; для одного seed ru и en совпадают по числам."""
import json, os, sys
from closebench.world import World
from closebench.strings import T, LANGS

def build_pack(seeds=range(1, 11), outdir="tasks", lang="en"):
    outdir = os.path.join(outdir, lang)
    os.makedirs(outdir, exist_ok=True)
    index = []
    for sd in seeds:
        w = World(seed=sd, lang=lang).build()
        snap, truth = w.snapshot(), w.truth()
        json.dump(snap, open(f"{outdir}/task_{sd:02d}_world.json", "w"), ensure_ascii=False, indent=1)
        json.dump(truth, open(f"{outdir}/task_{sd:02d}_truth.json", "w"), ensure_ascii=False, indent=1)
        index.append({"task": f"task_{sd:02d}", "seed": sd, "lang": lang, "period": snap["period"],
                      "entries": len(snap["entries"]), "documents": len(snap["documents"]),
                      "errors": len(truth["errors"]),
                      "error_kinds": [e["kind"] for e in truth["errors"]]})
    json.dump(index, open(f"{outdir}/index.json", "w"), ensure_ascii=False, indent=1)
    return index

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=LANGS, default="en")
    ap.add_argument("--outdir", default="tasks")
    a = ap.parse_args()
    idx = build_pack(outdir=a.outdir, lang=a.lang)
    print(json.dumps(idx[:2], ensure_ascii=False, indent=1))
    print(T(a.lang, "pack.total", n=len(idx)))
