# Pilot runs, 8 Oct 2026

Everything run while the lab was being built. Kept in full because the way it was built is part of the evidence, and
none of these numbers are published. The published numbers come only from `../final/`.

- `*-CONTAMINATED.jsonl`: Claude sessions that ran inside the repository and could read the repository, lab included .
- Runs before 10:45 AM ET used booking-reference version 1, a request with no flight number, so a careful model
  stopped to ask instead of booking and never had the fact the case measures. Version 2 fixed that.
- `*-STOPPED-thinking.jsonl`: the 14B model with its reasoning on, about five minutes a trial, stopped.
- `*-claude-haiku.jsonl` and `*-qwen3-14b.jsonl`: ran while the runner and the case file were being changed.
- `*-ministral-8b.*` and `*-gptoss-20b.*` from 12:04 PM and 12:50 PM ET: collected while their tool calls were
  replayed to the model with the arguments as escaped JSON text. Mistral's and OpenAI's templates both want
  an object there (and OpenAI's wants the result as an object too), checked against each vendor's format on
  8 Oct 2026. Rerun with the corrected encoding; these are kept to show the difference.
- `*-1332-llama-8b.*`: stopped at 20 of 60 by the responsiveness guard on a single momentary timeout while the 11 GB model was being swapped out; the guard now looks three times. Rerun.

Not in the public copy: `2026-10-08T0849-claude-mcp-CONTAMINATED.jsonl`, `2026-10-08T1017-claude-haiku.jsonl` and
`2026-10-08T1017-claude-sonnet.jsonl`. Those sessions ran before the full lockdown and their answers describe the
setup of the machine they ran on. Their numbers are not used anywhere. Every run in `../final/` ran
with one tool and nothing else, and its startup report on each row shows that.
