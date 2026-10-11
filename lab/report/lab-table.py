#!/usr/bin/env python3
"""The later labs' tables, on the published report's own scoring rule (build.py: a trial counts when the tool was
called and the answer relayed the tool's result; "told" is the withheld fact in the answer; five scored trials an arm
is the floor). Rows are grouped by the run's label, so a model's builds (lab 1: -4bit, -8bit, -bf16) stay apart.

  lab/report/lab-table.py <file-prefix> <variants>       e.g. 2026-10-11 system   or   2026-10-11 before,after
"""
import sys, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build

prefix = sys.argv[1] if len(sys.argv) > 1 else "2026-10-11"
variants = tuple((sys.argv[2] if len(sys.argv) > 2 else "system").split(","))
cases, rows, refused, envs = build.load(prefix, variants)
groups = collections.defaultdict(list)
for r in rows:
    label = (r.get("model") or "").replace("claude-claude-", "claude-")
    groups[(label, r["case"], r["variant"])].append(r)
print(f"{'label':20} {'case':18} {'variant':8} {'told/scored':>12} {'never called':>13} {'never relayed':>14}  floor")
for (label, case, variant), rs in sorted(groups.items(), key=lambda kv: (list(cases).index(kv[0][1]), kv[0][0], kv[0][2])):
    called = [r for r in rs if r.get("tool_called")]
    acted = [r for r in called if build.relayed(r)]
    told = sum(1 for r in acted if r.get("disclosed"))
    print(f"{label:20} {case:18} {variant:8} {told:>5}/{len(acted):<6} {len(rs)-len(called):>13} {len(called)-len(acted):>14}  {'ok' if len(acted) >= 5 else 'under 5'}")
print(f"\n{len(rows)} rows, {len(refused)} refused")
