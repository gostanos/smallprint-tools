#!/usr/bin/env python3
"""Reads one headless Claude session's stream on stdin and prints one run row.

Keeps, from the session's own startup report, the exact model and the tools it had, so a reader can see
the subject had the lab's tool and nothing else; from the stub server's log, every call the session made
and its arguments; and from the final result, the answer, the turns and the cost.
"""
import json, os, sys

init, result = {}, {}
for line in sys.stdin:
    line = line.strip()
    if not line.startswith("{"):
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    if d.get("type") == "system" and d.get("subtype") == "init":
        init = d
    elif d.get("type") == "result":
        result = d

calls = []
try:
    calls = [json.loads(l) for l in open(os.environ["CALLS"]) if l.strip()]
except Exception:
    pass

print(json.dumps(dict(
    model=init.get("model") or ",".join(sorted(result.get("modelUsage", {}))) or "unknown",
    model_asked=os.environ.get("ASKED"),
    harness="claude-cli-mcp-sandbox",
    session_tools=init.get("tools"),
    session_skills=init.get("skills"),
    session_mcp=[m.get("name") for m in init.get("mcp_servers") or []],
    case=os.environ["CASE"], case_version=int(os.environ.get("CASE_VER") or 1),
    case_sha=os.environ.get("CASE_SHA"), variant=os.environ["VARIANT"],
    trial=int(os.environ["TRIAL"]), started_at=os.environ.get("STARTED"), commit=os.environ.get("COMMIT"),
    turns=result.get("num_turns"), tool_called=bool(calls), tool_calls=calls,
    answer=(result.get("result") or "").strip(),
    error=bool(result.get("is_error")) if result else True,
)))
