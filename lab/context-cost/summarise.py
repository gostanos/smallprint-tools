#!/usr/bin/env python3
"""The figures the write-up quotes, read from results.json and nothing else.

For each server: its newest counted version (by publish date, then the order counted), that version's tools and
tokens, its first counted version's, and the change between them. Then what the newest versions cost per request on
each model, as tokens times the model's input price (Anthropic's pricing page, read 19 Oct 2026). Haiku 5.5 charges
$0.10 per million input tokens for a prompt up to 100,000 tokens and $0.50 for the whole prompt once it is over; the
other three charge one price across their context window. The four models count the same definitions to the same
number (checked 19 Oct 2026 on Hostinger 3.2.0, Desktop Commander 0.3.0 and Firecrawl 3.33.1: identical counts and the
same 286-token overhead). Prints Markdown tables.

  python3 lab/context-cost/summarise.py [results.json]
"""
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HAIKU_OVER_100K = 0.50
PRICES = {"Claude Haiku 5.5": 0.10, "Claude Sonnet 5.5": 2.00, "Claude Opus 5.5": 4.00, "Claude Fable 5.1": 10.00}  # $ per million input tokens


def method(r):
    # the box's result files are the run reader's reads, the same ones the record stores as run/100 with keys sorted
    # (checked 19 Oct 2026 on @playwright/mcp 0.0.83: same tools, descriptions and schemas)
    m = r.get("method", "?")
    return "run/100" if m == "run/runread" else m


def cost(tokens, model, price):
    """The tools' share of a request, priced as a request carrying only them would be."""
    if model == "Claude Haiku 5.5" and tokens > 100_000:
        price = HAIKU_OVER_100K
    return tokens * price / 1e6


def main():
    d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "results.json")))
    rows = d["rows"]
    by = {}
    for r in rows:
        by.setdefault(r["server"], []).append(r)
    counted = [r for r in rows if "tokens" in r]
    print(f"versions on file: {len(rows)}; counted: {len(counted)}; schema not fully read: {sum(r['schema_partial'] for r in rows)}; refused by the counter: {sum('rejected' in r for r in rows)}")
    print(f"from the run reader's files, not yet in the record: {sum(r.get('source') == 'runread' for r in counted)}")
    print(f"servers with a counted version: {sum(any('tokens' in r for r in v) for v in by.values())} of {len(by)}")
    print(f"tool-use overhead removed: {d['tool_use_overhead_tokens']} tokens; model {d['model']}\n")
    table = []
    for s, v in by.items():
        c = sorted([r for r in v if "tokens" in r], key=lambda r: r["published"] or "9999")
        if not c:
            continue
        last = c[-1]
        same = [r for r in c if method(r) == method(last)]
        first = same[0]
        table.append((s, len(c), first, last))
    table.sort(key=lambda t: -t[3]["tokens"])
    print("| Server | Versions counted | Earliest read the newest's way | Newest counted | Change | Read |")
    print("|---|---|---|---|---|---|")
    for s, n, f, l in table:
        ch = f"{l['tokens'] / f['tokens']:.1f}x" if f["tokens"] > 0 and f['version'] != l['version'] else "no earlier version read this way"
        print(f"| {s[4:]} | {n} | {f['version']} ({f['published']}): {f['tools']} tools, {f['tokens']:,} | {l['version']} ({l['published']}): {l['tools']} tools, {l['tokens']:,} | {ch} | {method(l)} |")
    # two npm names ship the same Hostinger server; the totals count it once
    newest = [t[3]["tokens"] for t in table if t[0] != "npm:@hostinger/mcp"]
    print(f"\nnewest versions: {len(newest)} servers; median {statistics.median(newest):,.0f} tokens; mean {statistics.mean(newest):,.0f}; sum {sum(newest):,}")
    for lim in (1000, 5000, 10000, 20000, 50000):
        print(f"  over {lim:,}: {sum(x > lim for x in newest)}")
    grew = [(t[0], t[2]["tokens"], t[3]["tokens"]) for t in table if t[2]["version"] != t[3]["version"] and t[0] != "npm:@hostinger/mcp"]
    print(f"servers with two versions read the same way: {len(grew)}; grew: {sum(b > a for _, a, b in grew)}; shrank: {sum(b < a for _, a, b in grew)}; same: {sum(b == a for _, a, b in grew)}")
    print("\n| Server | Newest tokens | " + " | ".join(PRICES) + " |")
    print("|---|---|" + "---|" * len(PRICES))
    for s, n, f, l in table[:10]:
        print(f"| {s[4:]} | {l['tokens']:,} | " + " | ".join(f"${cost(l['tokens'], m, p):.4f}" for m, p in PRICES.items()) + " |")
    print(f"\nall {len(newest)} newest versions together, per request: " + ", ".join(f"{m} ${cost(sum(newest), m, p):.2f}" for m, p in PRICES.items()))
    rej = [r for r in rows if "rejected" in r]
    if rej:
        print("\nrefused by the counter: " + "; ".join(f"{r['server'][4:]}@{r['version']}" for r in rej))


if __name__ == "__main__":
    main()
