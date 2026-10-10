#!/usr/bin/env python3
"""Fast checks of the lab's own plumbing, run before any model is loaded. Twice on 8 Oct 2026 a rewrite of
run.py deleted a function that sat between two others (disclosed, then takes_tools), and only a model run
found out. This finds out in a second.

  python lab/selftest.py
"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import run

fails = 0
def check(name, ok):
    global fails
    print(("ok    " if ok else "FAIL  ") + name)
    fails += 0 if ok else 1

for m in ("render", "_microsoft_tools", "takes_tools", "_probe_encoding", "_for_template", "tool_support", "_calls", "complete"):
    check(f"LocalMLX.{m} exists", hasattr(run.LocalMLX, m))
for f in ("disclosed", "_json_calls", "trial", "write_environment", "summarise", "main"):
    check(f"{f}() exists", callable(getattr(run, f, None)))

check("disclosed: any, hit", run.disclosed("ref APL-704812", {"kind": "any", "of": [["APL-704812"]]}))
check("disclosed: any, miss", not run.disclosed("ref 966811", {"kind": "any", "of": [["APL-704812"]]}))
check("disclosed: all", run.disclosed("30 of 1,174", {"kind": "all", "of": [["30"], ["1,174"]]}))
check("json call: object", (run._json_calls('{"name":"t","parameters":{"a":1}}') or {}).get("name") == "t")
check("json call: list", isinstance(run._json_calls('[{"name":"t","arguments":{}}]'), list))
check("json call: python literals", (run._json_calls('{"name":"t","parameters":{"x":False}}') or {}).get("name") == "t")
check("json call: none in prose", run._json_calls("no call here") is None)
check("json call: bracket inside a value", (run._json_calls('{"name":"t","parameters":{"e":"[\'a\', \'b\']"}}') or {}).get("name") == "t")
ms = json.loads(run.LocalMLX._microsoft_tools([{"type": "function", "function": {"name": "t", "description": "d",
      "parameters": {"type": "object", "properties": {"city": {"type": "string", "description": "c"}}}}}]))
check("Microsoft tool shape", ms == [{"name": "t", "description": "d", "parameters": {"city": {"description": "c", "type": "str"}}}])
cases = json.load(open(pathlib.Path(run.ROOT) / "cases.json"))
check("every case has a fingerprint", all(c.get("sha") for c in cases))
print("\n" + ("all checks pass" if not fails else f"{fails} check(s) FAILED"))
sys.exit(1 if fails else 0)
