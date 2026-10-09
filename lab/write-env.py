#!/usr/bin/env python3
"""Writes the environment of a Claude run beside its run file, so a reader can run the same thing."""
import json, subprocess, sys

out, trials, model, root = sys.argv[1:5]
sh = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
json.dump(dict(run_file=out.rsplit("/", 1)[-1], commit=sh(f"git -C {root} rev-parse --short HEAD"),
               harness="claude-cli-mcp-sandbox", claude_cli=sh("claude --version"), node=sh("node --version"),
               chip=sh("sysctl -n machdep.cpu.brand_string"),
               model_asked=model, trials_per_arm=int(trials),
               refused_tools="Read Write Edit Bash Glob Grep Task WebFetch WebSearch NotebookEdit",
               working_directory="an empty temporary directory, removed after the run",
               cases_sha={c["id"]: c.get("sha") for c in json.load(open(f"{root}/cases.json"))}),
          open(out.replace(".jsonl", ".env.json"), "w"), indent=1)
