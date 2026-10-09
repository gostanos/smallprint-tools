#!/usr/bin/env python3
"""Score a run file. Takes JSONL with case, variant and answer on each line, applies each
case's check from cases.json, and prints how many answers told the user the fact the newer text says not to mention.
Adds a `disclosed` field in place, so a run captured by any arm is scored the same way.

  tools/lab/score.py tools/lab/runs/<file>.jsonl
"""
import json, pathlib, sys
from run import disclosed

ROOT = pathlib.Path(__file__).resolve().parent


def main(path):
    cases = {c["id"]: c for c in json.load(open(ROOT / "cases.json"))}
    rows = [json.loads(l) for l in open(path) if l.strip().startswith("{")]
    for r in rows:
        if "disclosed" not in r:
            r["disclosed"] = disclosed(r.get("answer") or "", cases[r["case"]]["check"])
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    blank = sum(1 for r in rows if not (r.get("answer") or "").strip())
    print(f"{'case':<20} {'fact the newer text says not to mention':<46} {'before':>7} {'after':>6}")
    for cid in dict.fromkeys(r["case"] for r in rows):
        cells = {}
        for v in ("before", "after"):
            rs = [r for r in rows if r["case"] == cid and r["variant"] == v
                  and (r.get("answer") or "").strip()]
            cells[v] = f"{sum(1 for r in rs if r['disclosed'])}/{len(rs)}" if rs else "none"
        print(f"{cid:<20} {cases[cid]['withheld'][:46]:<46} {cells['before']:>7} {cells['after']:>6}")
    print(f"\n{len(rows)} trials, {blank} with no answer"
          )


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else sys.exit("pass a run file"))
