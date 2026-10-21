# What MCP tool definitions cost

How many tokens the tool definitions of the 50 most-downloaded MCP servers on npm cost a model, version by version. Written up at https://smallprint.dev/blog/what-mcp-servers-cost.

## The servers

`candidates.json` is every npm package in Small Print's record that was considered, sorted by weekly downloads (as of 18 Oct 2026), with the reason each one is in or out. A package is in when its npm description calls it an MCP server. Seven MCP servers whose descriptions don't say so were added by hand, and a proxy, two extensions and a toolkit were left out by hand. `servers.txt` is the 50 with the most downloads.

## The count

`count.py` sends each version's tools (name, description, input schema) to Anthropic's token counter on Claude Haiku 5.5, and takes away the same one-word message with no tools and the fixed instructions Anthropic adds whenever a request has tools (286 tokens, measured each run). A version is skipped when one of its input schemas could not be read in full. Sonnet 5.5, Opus 5.5 and Fable 5.1 gave the same counts on the three servers checked, so other models' costs are the count times their price.

The tools come from Small Print's record, so the script reads a copy of that database (`SMALLPRINT_DB`). The record reads a version's tools from the published package, or starts the package in a container with no network and no keys and asks it for its tools. Every row of `results.json` says which (`method`), because two versions read different ways can differ for reasons that are the reader's, not the server's. A change between versions is only quoted when both were read the same way.

`summarise.py` turns `results.json` into the tables in the write-up.

`results.json` holds names, versions, tool counts and token counts, and no tool text.
