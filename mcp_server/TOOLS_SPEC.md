# Python MCP Tools: File-by-File Specification

This document describes the intended responsibility of every module in `burp_mcp/tools/`. It is a guide for implementing the Python layer; it does not replace the Kotlin implementation.

## Architecture

The Kotlin extension runs inside Burp and owns all Burp/Montoya behavior. It already implements and registers the 30 Burp tools. The Python process is an MCP server over stdio and an MCP client to the extension over SSE:

```text
Claude Code --stdio--> Python MCP server --SSE/JSON-RPC--> Kotlin extension in Burp --> Montoya API
```

Python has three possible roles:

1. **Generic passthrough:** list and invoke any Kotlin tool by name.
2. **Typed wrappers:** expose selected Kotlin tools as individually named Python MCP tools, forwarding arguments to the matching Kotlin tool.
3. **Python-only tools:** perform local analysis, transformation, formatting, or orchestration that does not replace Burp's behavior.

The direct Claude command `claude mcp add --transport sse wenaco http://127.0.0.1:9262/` connects directly to Kotlin. That path does not load or use the Python modules described here. Use the Python server when you want Claude to launch an stdio process, want Python-only functionality, or want typed wrapper tools.

## Shared Wrapper Contract

Every typed wrapper module should export `register(mcp)`. For each Kotlin-backed operation, registration should define an MCP tool whose public name is the same as the Kotlin tool name. A wrapper should:

1. Use the Kotlin tool's `inputSchema` as the source of truth for argument names, types, required fields, and allowed values. The schema can be read from the Kotlin implementation or fetched through `list_burp_tools` while Burp is running.
2. Use Python type hints and a clear docstring so the Python MCP SDK publishes a useful schema to Claude. Keep that signature consistent with Kotlin's schema.
3. Create/use `BurpProxy`, call the matching Kotlin tool name with its arguments, and return the result. Do not recreate Burp actions in Python.
4. Preserve Kotlin errors/results, including structured content when present. Do not silently convert an error to a success-shaped string.
5. Avoid retries around traffic-producing calls. A retry may send the same request twice or start duplicate scans.

The extension remains the authority for scope and ROE checks. Python wrappers must not bypass them, perform the same traffic directly with `httpx`, or claim that a Python-side check replaces the Kotlin guard.

The MCP SDK builds JSON schemas from Python signatures, so there is no safe general conversion from the arbitrary JSON Schema received from Kotlin into named Python function signatures. This is why the explicit wrappers are written individually and the generic passthrough remains available as a fallback.

## Existing Modules

### `burp_passthrough.py` - implemented

Registers two generic tools:

- `list_burp_tools`: asks the Kotlin extension for its current tool names, descriptions, and schemas.
- `call_burp_tool`: calls one extension tool by exact name with an arguments object matching that tool's schema.

Keep this available even after adding typed wrappers. It is the fallback for new Kotlin tools that do not yet have Python wrappers and the best way to inspect the live schema. It requires a loaded Burp extension when invoked.

### `transform_tool.py` - implemented, pure Python

Registers `transform_text`, which handles the existing standalone string encode/decode operations. It does not connect to Burp. Keep its name distinct from Kotlin's `transform` tool, which is registered by `burp_utility_tools.py`.

When extending this utility, validate malformed inputs and unsupported operation names with clear errors. Do not imply JWT signature validation: decoding a JWT payload is not verification.

## Kotlin-Backed Typed Wrapper Modules

All modules below should define `register(mcp)`, register only their listed operations, and forward each operation to Kotlin through `BurpProxy`. The listed names describe the intended interface; check exact Kotlin schemas before implementing or changing parameters.

### `http_tools.py` - currently empty

Expose HTTP sending and request-history inspection:

- `send_http_request`: send one request using Kotlin's request-building and scope/ROE behavior.
- `send_http_requests`: send a supplied batch and return Kotlin's per-request results.
- `get_proxy_history`: query Burp Proxy HTTP history and forward its supported filters.
- `get_proxy_entry`: retrieve request/response data for the supplied history index.
- `get_websocket_history`: retrieve and filter WebSocket history.

Sending is performed only by the Kotlin extension. Do not use Python HTTP libraries as an alternate path.

### `scan_tools.py` - currently empty

Expose Burp scan, crawl, and scan-result operations:

- `start_active_scan`: request an active audit using a URL or request representation supported by Kotlin; the extension enforces scope.
- `passive_scan`: start the Kotlin passive-audit operation.
- `start_crawl`: start a crawl from a seed URL; preserve the extension's stated seed/scope semantics.
- `scan_status`: return the status for a scan or the Kotlin-supported list of scans.
- `stop_scan`: stop the identified scan.
- `get_scanner_issues`: return findings, preserving Kotlin filters and structured results.
- `generate_report`: forward report parameters to the Burp implementation; do not pretend the Python report formatter is the same operation.

Scanner-related operations may require Burp Suite Professional. Surface the extension error rather than failing silently.

### `fuzz_tools.py` - currently empty

Expose `fuzz` by forwarding the exact Kotlin input schema. The extension generates requests, applies its scope guard, and runs its native fuzzer. Do not implement a second fuzzer or send payloads from Python. Keep payload sets, markers, concurrency, filters, and limits consistent with the live Kotlin schema.

### `send_to_tools.py` - currently empty

Expose the operations that stage items in Burp tools:

- `send_to_repeater`
- `send_to_intruder`
- `send_to_organizer`
- `send_to_comparer`

These forward the Kotlin arguments. Staging a request in Intruder is not the same as launching an Intruder attack; explain the actual Kotlin behavior in the wrapper descriptions.

### `scope_tools.py` - missing; `server.py` currently imports it

Create this module and expose:

- `scope_check`: ask Burp whether a URL is in its Target scope.
- `scope_add`: add a supported URL prefix to Burp scope.
- `scope_remove`: remove a supported URL prefix from Burp scope.
- `sitemap_query`: query Burp's site map with Kotlin-supported filters.

Do not implement a separate Python scope model. The Kotlin extension and Burp Target settings are authoritative. Until this module exists and defines `register(mcp)`, importing `burp_mcp.server` will fail because `server.py` currently imports `scope_tools`.

### `collaborator_tools.py` - currently empty

Expose:

- `generate_collaborator_payload`: request a payload from Burp Collaborator.
- `get_collaborator_interactions`: retrieve interactions visible to the current Burp Collaborator context.

Forward to Kotlin; do not invent or independently poll a Collaborator service in Python.

### `control_tools.py` - currently empty

Expose:

- `import_bcheck`: forward source/path arguments accepted by Kotlin.
- `set_intercept`: enable or disable Burp Proxy interception as supported by Kotlin.
- `set_task_engine`: change Burp's task-engine state using the Kotlin-supported values.

These alter Burp state. Use accurate descriptions and preserve the extension's validation and any guards.

### `config_tools.py` - currently empty

Expose:

- `export_burp_config`: forward export scope, path, and selection options supported by Kotlin.
- `import_burp_config`: forward import source/options supported by Kotlin.

Configuration import changes Burp state and is guarded by the extension. Do not bypass that guard or write directly into Burp configuration from Python.

### `burp_utility_tools.py` - currently empty

Expose Kotlin's `transform` and `random_string` operations:

- `transform`: call the Kotlin utility with the exact operation/input fields from its schema.
- `random_string`: request a generated string using Kotlin's supported parameters.

This module connects to Burp via `BurpProxy`, unlike `transform_tool.py`, which is a pure Python utility called `transform_text`.

## Python-Only Modules

These modules exist as empty placeholders. They are optional additions, not required to call the 30 Kotlin tools. If implemented, each should define `register(mcp)` and be explicitly imported and registered in `server.py`. Keep their proposed behavior small and deterministic.

### `workflow_tools.py` - registered

Use for named, multi-step convenience workflows that compose existing Kotlin calls through `BurpProxy`; do not create new network behavior. The current `scan_results_workflow` accepts an existing `scan_id`, calls Kotlin `scan_status` and `get_scanner_issues`, and returns both results. It does not start or poll scans.

Workflow input should make side effects explicit. Return constituent results and identifiers so the user can see what ran. Do not automatically fuzz, actively scan, alter configuration, or send batches without a clear user invocation.

### `analysis_tools.py` - empty and not registered

Use for local interpretation of data the caller supplies or receives from Burp. Suitable examples:

- Summarize selected proxy-history rows or scanner findings.
- Compare two supplied HTTP responses for status/header/body differences.
- Normalize or group findings by host, severity, or evidence.

Keep analysis honest: do not invent findings, infer vulnerability solely from a status code, or claim a request was sent unless a Kotlin result confirms it. Bound output size and avoid logging sensitive request/response data.

### `report_tools.py` - empty and not registered

Use for formatting caller-supplied or Burp-returned evidence into a report template (for example Markdown with title, affected URL, impact, reproduction, evidence, and remediation). Preserve the source evidence and distinguish user-provided claims from observed results. Do not fabricate impact or severity. Prefer returning text to the caller; file-writing should be an explicit option with a validated destination.

Kotlin's `generate_report` is a separate Burp Scanner report operation and remains in `scan_tools.py`.

## `server.py` Registration Rules

`mcp_server/burp_mcp/server.py` creates the MCP server and calls each registered module's `register(mcp)` once. The typed Kotlin wrapper modules and the generic passthrough are needed for the current Python-server design. The pure-Python `transform_tool` is also registered.

The Python-only `analysis_tools` and `report_tools` should be registered only after they contain working tools. Keep every registered MCP tool name unique. The standalone `transform_text` and Kotlin-backed `transform` are intentionally distinct.

The wrapper modules and `scope_tools.py` are implemented and registered. The Python server exposes 34 unique tools: the 30 Kotlin-backed wrappers, two passthrough tools, `transform_text`, and `scan_results_workflow`.

## Verification and Optional Follow-up

1. Run Python unit tests from `mcp_server`:

   ```sh
   .venv/bin/python -m unittest discover -s tests -v
   ```

2. With Burp and the extension running, call `list_burp_tools` and verify the live Kotlin inventory. Exercise only harmless tools during a smoke test.
3. Optional analysis/report tools may be added after defining their concrete use case; register and test each one.

Python wrapper tests cannot prove the Kotlin implementation is correct; retain the Kotlin unit/integration suite and test traffic-producing behavior only against an authorized in-scope lab.
