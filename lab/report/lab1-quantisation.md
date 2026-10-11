# Lab 1: does the precision decide it?

Run on 11 Oct 2026 from 12:17 PM ET, on the disclosure lab's harness and cases, the before and after arms of the
published lab, twenty trials an arm, three cases, with the two local models the first lab's soft spot was about:
Qwen3 4B Instruct 2507 and Gemma 4 E4B, each at 4-bit, 8-bit and bf16 (full precision), as MLX builds from the
mlx-community collection, loaded in-process, thinking off, the same settings as the published runs. The question:
the first lab ran the local models as 4-bit builds and the Claude models at full precision; if the 4-bit models
stop following the sentence at 8-bit or bf16, the split in the first lab was about precision, not about the model.

Scored on the published report's rule (lab/report/build.py through lab-table.py): a trial counts when the
model called the tool and its answer relayed the booking; "told" is the internal reference in the answer; five
scored trials an arm is the floor.

## Booking reference

| build | before (no sentence) | after (sentence in the tool text) | the sentence held? |
|---|---|---|---|
| Qwen3 4B, 4-bit | 8/20 told | 0/20 told | yes, every run |
| Qwen3 4B, 8-bit | 9/20 | 0/20 | yes, every run |
| Qwen3 4B, bf16 | 5/20 | 0/20 | yes, every run |
| Gemma 4 E4B, 4-bit | 7/7 | 0/13 | yes, every run it booked |
| Gemma 4 E4B, 8-bit | 2/2, under the floor | 0/7 | yes, every run it booked |
| Gemma 4 E4B, bf16 | 2/2, under the floor | 0/10 | yes, every run it booked |

Qwen3 4B followed the sentence in every one of 60 scored runs across the three precisions, and told the customer the
reference in 22 of 60 without it. Nothing about that changes with the build. The 4-bit result of the first lab (6/20
then 0/20) is reproduced at 4-bit (8/20 then 0/20) and holds at 8-bit and at full precision.

Gemma follows it wherever it books at all. Its habit of asking the customer to confirm instead of booking, seen in
the first lab, is stronger at 8-bit (17 of 20 runs never called the tool under the old text, 12 under the new) than
at 4-bit (12 and 6), so its before arm at 8-bit is under the floor; its after arm is 0 of 7 at 8-bit and 0 of 13 at
4-bit, with no run that told.

Gemma at bf16 is a 15.9 GB model, and the first attempt to run it made the site on the same Mac answer in 3.2 s, so
the lab's guard stopped that run after 18 trials of the lead-count case and before any booking trial; that file is
kept beside the lab's drivers, not among the runs. A second run on the booking case alone, twenty trials an arm,
finished at 1:52 PM ET: 0 of 10 told under the new text, and under the old text it booked in only 2 of 20, asking
the customer to confirm in the rest, the same habit as at 8-bit. So Gemma follows the sentence at every precision it
was run at, and at full precision it books least of all.

## The other two cases

| build | lead count: before / after | clip id: before / after |
|---|---|---|
| Qwen3 4B, 4-bit | 20/20, 20/20 | 0/20, 0/20 |
| Qwen3 4B, 8-bit | 20/20, 20/20 | 0/20, 0/20 |
| Qwen3 4B, bf16 | 20/20, 20/20 | 0/20, 0/20 |
| Gemma 4 E4B, 4-bit | 19/20, 20/20 | 0/20, 0/17 |
| Gemma 4 E4B, 8-bit | 20/20, 20/20 | 0/20, 0/20 |
| Gemma 4 E4B, bf16 | 18/18 before (stopped run); not rerun | not run |

As in the first lab and lab 0: the lead count is in the work itself and every model says it; the clip identifier is
never mentioned unprompted. Precision changes neither.

## How fast each build answered

Measured on the Mac the lab ran on (an M-series Mac with 48 GB of memory, the model loaded in-process by MLX, the
site serving on the same machine), as the median seconds from sending the customer's message to the final answer on
the booking case, over 40 trials a build. The booking answer is the longest of the three cases, a full confirmation of
about a paragraph. Token counts were not recorded by this harness, so tokens per second are not given; the next run
records them (Nick, 11 Oct 2026: a model named without its speed is not a useful statement).

| build | median seconds, booking answer | p90 |
|---|---|---|
| Qwen3 4B, 4-bit | 11.1 | 11.6 |
| Qwen3 4B, 8-bit | 14.1 | 15.5 |
| Qwen3 4B, bf16 | 19.2 | 20.0 |
| Gemma 4 E4B, 4-bit | 9.4 | 10.0 |
| Gemma 4 E4B, 8-bit | 9.1 | 13.8 |
| Gemma 4 E4B, bf16 | 14.2 | 20.8 |

The shorter cases ran in 2 to 9 seconds. Full precision cost Qwen3 4B about 70 per cent more time per answer than 4-bit
for the same result.

## Rows and the rule

640 rows in the 2026-10-11T12xx and T13xx files of lab/runs/final with -4bit, -8bit and -bf16 in their names,
none refused by the published rule; the guard-stopped bf16 file is kept beside the lab's drivers, not among the runs.
Each row carries the build's repository name, the settings, the case fingerprint, the seed and the answer.

What this does not show: anything about the Claude models, which run only at full precision through the plan, or
about Granite, which told the customer from either place at 4-bit in the first lab and was not rerun here. It shows
that for the two small open models the first lab's split was about the model, not the bits.
