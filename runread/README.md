# Run reads

Each file under `results/npm/<name>/<version>.json` is one read of one published npm package version by Small Print's run reader: the package was installed with scripts off, started inside a container with no network, no capabilities and a read-only root, and asked for its tools with the official MCP client. A tool is never called. The file holds the tools as served, the server's own name and protocol version, the integrity of what was installed, the command and environment names used (placeholder values only), the first bytes of the server's stderr, how long it took, and the image and SDK versions. `log/box.log` is the reader's own log, one line per read.

A file with a status other than `tools` says why there is no tool list: `no-bin` (the package has no executable), `exit` (it stopped before answering; the stderr says what it wanted), `needs-config` (it named a key or setting), `timeout`, `install-failed`, `not-mcp`.

The reader's source is `apps/runread` in the Small Print repository. These files are what the entry pages at https://smallprint.dev link as the read's log; the record never replaces a static read with a run read, and never compares the two.
