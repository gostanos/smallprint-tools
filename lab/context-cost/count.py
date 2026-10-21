#!/usr/bin/env python3
"""How many tokens the tool definitions of the 50 most-downloaded MCP servers on npm cost a model, version by version.

For each server in servers.txt and each of its versions whose tools Small Print read in full (every input schema
followed), the tools are sent to Anthropic's token counter exactly as a client would hand them to Claude: name,
description and input schema. What a server's tools cost is the count with them, minus the same one-word message with no
tools, minus the fixed instructions Anthropic adds once whenever a request has any tools at all (measured each run as one
empty tool's count less 35 tokens for the empty tool itself, about 286 tokens on 18 Oct 2026), so a number is the
server's own definitions. Token counting is free (Anthropic's docs, read 18 Oct 2026); it
runs on one model, Claude Haiku 5.5, the cheapest (Nick, 18 Oct 2026), and the cost of those tokens on other models is
the count times each model's price, not a second count.

Where the tools come from: Small Print's read API (https://smallprint.dev/api/asset/npm/<name>?all=1 for the versions),
or, on the Mac that holds the record, the record itself with --local. With --runread DIR, a version the record has no
tools for yet is taken from the run reader's own result file (DIR/npm/<name>/<version>.json, status "tools", the same
files published nightly to gostanos/smallprint-tools under runread/results), marked "source": "runread"; the box reads
that finish after the 12:50 AM pull reach the record a night later. The tool text stays out of this repository;
results.json keeps names, versions and counts, and how each version's tools were read ("method": the record's extraction
and reader revision), since two versions read different ways can differ for reasons that are the reader's, not the
server's; a change is only quoted between versions read the same way.

  SMALLPRINT_DB=<path to the record> [SMALLPRINT_DB_USER=<account>] python3 lab/context-cost/count.py --local [--runread DIR] [--servers lab/context-cost/servers.txt]
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = "claude-haiku-5-5"
# the record: a SQLite copy of Small Print's database, read-only; SMALLPRINT_DB_USER, when set, is the account that may
# read it (the command runs as that account through sudo)
DB = os.environ.get("SMALLPRINT_DB", "smallprint.db")
DB_USER = os.environ.get("SMALLPRINT_DB_USER", "")


def sqlite_json(q):
    cmd = ["sqlite3", "-readonly", "-json", DB, q]
    if DB_USER:
        cmd = ["sudo", "-n", "-H", "-u", DB_USER] + cmd
    return json.loads(subprocess.run(cmd, capture_output=True, text=True, cwd="/").stdout or "[]")
API = "https://api.anthropic.com/v1/messages/count_tokens"


def key():
    with open(os.path.expanduser("~/.config/smallprint/lab.env")) as f:
        for line in f:
            m = re.match(r'^ANTHROPIC_API_KEY="(.*)"\s*$', line.strip())
            if m:
                return m.group(1)
    sys.exit("no key in ~/.config/smallprint/lab.env")


def count(k, tools):
    body = {"model": MODEL, "messages": [{"role": "user", "content": "hi"}]}
    if tools:
        body["tools"] = tools
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST",
                                 headers={"x-api-key": k, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)["input_tokens"]
        except urllib.error.HTTPError as e:
            if e.code in (429, 529, 500, 503):
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]!r}")
    raise RuntimeError("token counter kept refusing")


def anthropic_tool(t):
    schema = t.get("inputSchema") or {"type": "object", "properties": {}}
    if not isinstance(schema, dict) or schema.get("type") != "object":
        schema = {"type": "object", "properties": {}}
    return {"name": re.sub(r"[^a-zA-Z0-9_-]", "_", t["name"])[:128], "description": t.get("description") or "", "input_schema": schema}


def local_versions(cn):
    q = ("select v.version, v.published_at, v.tools_json, v.extraction, v.reader_rev from asset_versions v join assets a on a.id = v.asset_id "
         f"where a.canonical_name = '{cn}' and v.tools_json is not null and json_array_length(v.tools_json) > 0 order by v.published_at")
    return sqlite_json(q)


def runread_versions(d, cn, have):
    """Versions the run reader listed tools for that the record does not have yet."""
    import glob
    q = ("select v.version, v.published_at from asset_versions v join assets a on a.id = v.asset_id "
         f"where a.canonical_name = '{cn}'")
    dates = {r["version"]: r["published_at"] for r in sqlite_json(q)}
    out = []
    for f in glob.glob(os.path.join(d, "npm", cn[len("npm:"):], "*.json")):
        r = json.load(open(f))
        if r.get("status") == "tools" and r.get("tools") and r["version"] not in have:
            out.append({"version": r["version"], "published_at": dates.get(r["version"]) or "", "tools_json": json.dumps(r["tools"]), "source": "runread",
                        "extraction": "run", "reader_rev": "runread"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--servers", default=os.path.join(HERE, "servers.txt"))
    ap.add_argument("--local", action="store_true")
    ap.add_argument("--runread", help="a copy of the run reader's results folder")
    ap.add_argument("--out", default=os.path.join(HERE, "results.json"))
    a = ap.parse_args()
    if not a.local:
        sys.exit("only --local is written so far")
    k = key()
    base = count(k, None)
    empty = {"name": "x", "description": "", "input_schema": {"type": "object", "properties": {}}}
    one, two = count(k, [empty]), count(k, [empty, dict(empty, name="y")])
    overhead = one - base - (two - one)  # the fixed tool-use instructions, without the empty tool itself
    rows = []
    for cn in [l.strip() for l in open(a.servers) if l.strip()]:
        versions = local_versions(cn)
        if a.runread:
            versions += runread_versions(a.runread, cn, {v["version"] for v in versions})
        for v in versions:
            tools = json.loads(v["tools_json"])
            partial = any(t.get("inputSchemaNotFollowed") or t.get("inputSchemaFieldsNotFollowed") for t in tools)
            row = {"server": cn, "version": v["version"], "published": (v["published_at"] or "")[:10], "tools": len(tools), "schema_partial": partial,
                   "source": v.get("source", "record"), "method": f"{v.get('extraction') or ''}/{v.get('reader_rev') or ''}"}
            if not partial:
                try:
                    row["tokens"] = count(k, [anthropic_tool(t) for t in tools]) - base - overhead
                except RuntimeError as e:
                    # the API refuses the definitions as the server ships them (for example a schema that is not valid
                    # JSON Schema 2020-12); kept as a finding, not repaired, since a repair would be a guess at a client's
                    row["rejected"] = str(e)[:400]
            rows.append(row)
        print(f"{cn}: {len(versions)} versions with tools", flush=True)
    json.dump({"model": MODEL, "baseline_tokens": base, "tool_use_overhead_tokens": overhead, "counted_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "rows": rows}, open(a.out, "w"), indent=1)
    print(f"{len(rows)} versions, {sum('tokens' in r for r in rows)} counted; written {a.out}")


if __name__ == "__main__":
    main()
