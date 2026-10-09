#!/usr/bin/env node
// A stub MCP server for the disclosure lab. It serves one tool out of tools/lab/cases.json,
// with the description from whichever version the run is testing, and answers every call with
// that case's canned result. Nothing is fetched, nothing is written, no package code runs.
//
// Picked by environment:
//   LAB_CASE=booking-reference   LAB_VARIANT=before|after
//
// This exists so the description reaches the model the way a real one does, through the tool
// list of a real MCP server, rather than as text pasted into a prompt.
import { readFileSync, appendFileSync } from "node:fs";
import { createInterface } from "node:readline";

const cases = JSON.parse(
  readFileSync(new URL("../cases.json", import.meta.url), "utf8"));
const c = cases.find((x) => x.id === (process.env.LAB_CASE || cases[0].id));
if (!c) { console.error("no such case"); process.exit(2); }
const variant = process.env.LAB_VARIANT === "after" ? "after" : "before";
const description = variant === "after" ? c.description_after : c.description_before;

const send = (m) => process.stdout.write(JSON.stringify(m) + "\n");
const reply = (id, result) => send({ jsonrpc: "2.0", id, result });

createInterface({ input: process.stdin }).on("line", (line) => {
  if (!line.trim()) return;
  let m;
  try { m = JSON.parse(line); } catch { return; }
  if (m.method === "initialize") {
    return reply(m.id, {
      protocolVersion: "2024-11-05",
      capabilities: { tools: {} },
      serverInfo: { name: "smallprint-lab-stub", version: "1.0.0" },
    });
  }
  if (m.method === "tools/list") {
    return reply(m.id, {
      tools: [{ name: c.tool.name, description, inputSchema: c.tool.parameters }],
    });
  }
  if (m.method === "tools/call") {
    if (process.env.LAB_LOG) {
      appendFileSync(process.env.LAB_LOG, JSON.stringify({
        name: m.params?.name, arguments: m.params?.arguments ?? {} }) + "\n");
    }
    return reply(m.id, {
      content: [{ type: "text", text: JSON.stringify(c.tool_result) }],
    });
  }
  if (m.method === "resources/list") return reply(m.id, { resources: [] });
  if (m.method === "prompts/list") return reply(m.id, { prompts: [] });
  if (m.id !== undefined) reply(m.id, {});
});
