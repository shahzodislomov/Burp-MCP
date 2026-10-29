# Wenaco Burp MCP: Implementation Specification

This document records the implementation plan and extension guidance. The Python wrapper work described below is now implemented; the remaining guidance applies to future changes and live integration checks.

Implementation status (2026-10-29): the Python stdio server exposes all 30 typed Kotlin wrappers plus `list_burp_tools`, `call_burp_tool`, `transform_text`, and `scan_results_workflow` (34 tools total). Bearer-token headers and structured results are supported. Offline `unittest` coverage passes. A live Burp connection check still requires Burp with the extension loaded.

The existing Kotlin extension registers 30 tools. Do not rewrite those tools just to make this project feel complete. The wrapper layer and offline tests are implemented; remaining verification is the live Burp smoke test, followed by any capabilities specific to your use case.

## 1. Choose the Client Path

There are two paths. They are alternatives, not two hops in the same connection:

### Direct to the Burp extension

```sh
claude mcp add --transport sse wenaco http://127.0.0.1:9262/
claude mcp add --transport sse wenaco http://127.0.0.1:9262/ --header "Authorization: Bearer SECRET"
```

This connects the MCP client straight to the Kotlin extension running inside Burp. The client sees the 30 Kotlin tools by their individual names. The Python server and its wrappers are not involved. Use this path if the direct SSE command is the product experience you want users to have.

### Through the Python server

```sh
cd mcp_server
claude mcp add wenaco -- python3 /absolute/path/to/burp-mcp/mcp_server/start_server.py
```

This starts the Python server over stdio. The launcher selects the project's virtual environment and working directory. Python connects to the Burp extension at `BURP_MCP_URL` and exposes all 30 Kotlin tools by their individual names, plus `list_burp_tools`, `call_burp_tool`, the standalone `transform_text` utility, and `scan_results_workflow`.

If you implement the wrappers in this plan, the Python path can expose the 30 Burp operations individually. Keep both paths only if you want to support both experiences. Do not configure two servers with the same client-side name at once; choose one connection method per client configuration.

## 2. Current State

- `extension/src/main/kotlin/me/wenaco/burpmcp/BurpMcpExtension.kt` registers 30 Kotlin tool implementations.
- `extension/src/main/kotlin/me/wenaco/burpmcp/mcp/` contains the MCP transport, JSON-RPC dispatcher, registry, protocol models, and tool contract. The transport supports legacy SSE and Streamable HTTP.
- Kotlin tool implementations and unit/integration tests already exist. Leave them in place; modify or add Kotlin only for a new Burp-side capability or a verified defect.
- `mcp_server/burp_mcp/burp_proxy.py` is the Python MCP client for the extension. It connects to `http://127.0.0.1:9262/` by default.
- `mcp_server/burp_mcp/server.py` registers the Python-facing tools and runs stdio under the MCP server name `wenaco`.
- `mcp_server/burp_mcp/tools/burp_passthrough.py` implements generic discovery and invocation of any extension tool.
- `mcp_server/burp_mcp/tools/transform_tool.py` implements a pure-Python transform utility.
- `mcp_server/burp_mcp/tools/` contains typed wrappers for all 30 Kotlin tools; the standalone utility is named `transform_text` to avoid colliding with Kotlin `transform`.
- Offline Python tests live in `mcp_server/tests/` and use `unittest`; runtime dependencies are declared in `mcp_server/requirements.txt`.
- The current `extension/docs/` folder contains `CONNECTING.md`. The architecture, extension-compatibility, and spec-maturity documents mentioned in older changelog text are not currently present there; do not treat an old changelog reference as a current implementation requirement.
- The extension uses Java toolchain 21. Keep that target; the Python server is a separate process and does not use the JVM.

## 3. Recommended Work Order

### Phase A: Preserve the working extension

Before adding wrappers, build and test the existing extension:

```sh
cd extension
./gradlew test shadowJar
```

Load the resulting jar into Burp and confirm its Output tab reports that the MCP server is ready. Confirm the live `tools/list` result has 30 tools. This is the baseline for later integration checks.

Do not rewrite the existing `Tool`, `ToolRegistry`, `Dispatcher`, `McpServer`, or 30 registered tools as part of the Python wrapper work. They are the Burp-side implementation and safety boundary.

### Phase B: Finish the Python interface (only needed for the Python stdio path)

Implement one typed Python wrapper for each Kotlin tool. A wrapper must forward to the Kotlin tool; it must not recreate Burp behavior in Python. Reuse `BurpProxy` and preserve the extension's scope checks and other safeguards.

For each wrapper:

1. Get the exact name, description, required fields, types, and input schema from the Kotlin tool's `inputSchema` or the live `list_burp_tools` result.
2. Define a Python function with type hints and a useful docstring. The MCP SDK uses these to publish the Python tool schema.
3. Open `BurpProxy` with its async context manager, call the exact Kotlin tool name with a matching arguments object, and return its result without silently changing its meaning.
4. Test the forwarding call, returned value, and error path using a fake proxy. Do not send network traffic in unit tests.

Use this module map. The total is 30 Kotlin-backed wrappers:

| Python module | Kotlin tools to wrap | Count |
|---|---|---:|
| `tools/http_tools.py` | `send_http_request`, `send_http_requests`, `get_proxy_history`, `get_proxy_entry`, `get_websocket_history` | 5 |
| `tools/scan_tools.py` | `start_active_scan`, `passive_scan`, `start_crawl`, `scan_status`, `stop_scan`, `get_scanner_issues`, `generate_report` | 7 |
| `tools/fuzz_tools.py` | `fuzz` | 1 |
| `tools/send_to_tools.py` | `send_to_repeater`, `send_to_intruder`, `send_to_organizer`, `send_to_comparer` | 4 |
| `tools/scope_tools.py` | `scope_check`, `scope_add`, `scope_remove`, `sitemap_query` | 4 |
| `tools/collaborator_tools.py` | `generate_collaborator_payload`, `get_collaborator_interactions` | 2 |
| `tools/control_tools.py` | `import_bcheck`, `set_intercept`, `set_task_engine` | 3 |
| `tools/config_tools.py` | `export_burp_config`, `import_burp_config` | 2 |
| `tools/burp_utility_tools.py` | Kotlin `transform`, `random_string` | 2 |
| **Total** | | **30** |

Do not guess arguments from a tool name. For example, use the actual Kotlin schema for `send_http_request`, `fuzz`, and configuration tools rather than inventing a smaller Python-only signature.

### Phase C: Register Python tools once

Update `mcp_server/burp_mcp/server.py` to:

- Set the Python MCP server name to `wenaco` if using the Python path.
- Import and call `register(mcp)` exactly once for every wrapper module above.
- Keep registering `burp_passthrough` so users retain a generic fallback and can inspect the live schemas.
- Ensure the final Python tool names are unique.

There is a collision to resolve: the pure-Python `transform_tool.py` currently registers a tool named `transform`, and the Kotlin extension also has a tool named `transform`. To expose all 30 Kotlin tools under their exact names while retaining the Python utility, rename the Python utility to `transform_text` and expose the Kotlin-backed operation as `transform`. Update its docstring and tests to match. Do not register duplicate `transform` names.

After this phase, the Kotlin-backed wrappers and passthrough/utility tools list 33 names. The registered `scan_results_workflow` adds one Python-only tool, for 34 unique names total.

### Phase D: Make Python connection configuration complete

Update `mcp_server/burp_mcp/burp_proxy.py` only as required to support the selected deployment:

- Keep `BURP_MCP_URL` with default `http://127.0.0.1:9262/`.
- Add optional `BURP_MCP_TOKEN` support so the Python client can send the bearer token when the extension was started with `-Dburpmcp.token=...`. Use the MCP SDK's supported SSE header mechanism; verify it against the pinned/range-supported SDK version.
- Keep connection failures actionable and avoid logging token values.
- Preserve MCP tool errors. If Kotlin returns structured content, expose it consistently rather than discarding it accidentally; confirm the SDK result shape before changing the return type.
- Retain context-manager cleanup on connection and call failures.

Do not add retries that repeat a traffic-producing Burp operation. A retry could send the same request or start the same scan twice.

### Phase E: Test and document

Create these Python tests:

| New file | What it verifies |
|---|---|
| `mcp_server/tests/test_tool_registration.py` | All expected Python tool names register exactly once; expected total is 34 including `scan_results_workflow`. |
| `mcp_server/tests/test_tool_wrappers.py` | Every wrapper forwards to the correct Kotlin name with the supplied arguments; results and errors are preserved. Use a fake `BurpProxy`. |
| `mcp_server/tests/test_burp_proxy.py` | Default/overridden URL, optional token header, failed initialization cleanup, and tool error handling. Do not assert or print secret values. |

Use `unittest` if you want to avoid adding a test dependency. If you choose `pytest`, add it as a development dependency and document the command. Add a separate opt-in live test only when Burp is running; it may list tools and call a harmless utility such as `random_string`, but must not send traffic to a target.

Update `mcp_server/README.md` after implementation so it describes the actual registered Python tool set, connection mode, token configuration, and test command. Keep the root README and `extension/docs/CONNECTING.md` consistent with the client command you intend users to use.

## 4. When a Kotlin File Is Needed

Only add Kotlin when the desired feature needs Montoya API access or must run inside Burp. For each new Burp capability:

1. Add `extension/src/main/kotlin/me/wenaco/burpmcp/tools/<NewTool>.kt` implementing the existing `Tool` contract. Give it a stable tool name, clear description, accurate JSON input schema, input validation, and a result that is useful to an MCP client.
2. Keep network traffic behind existing scope/ROE checks. Never let a new tool silently bypass them. Keep destructive or configuration-changing actions explicitly gated, following the existing config-edit pattern.
3. Register it once in `BurpMcpExtension.initialize`.
4. Add `extension/src/test/kotlin/me/wenaco/burpmcp/<NewTool>Test.kt`. Test argument validation and behavior that can be tested without a live Burp instance; add integration coverage only when Montoya behavior requires it.
5. Add a Python wrapper in the appropriate module and wrapper test only if the Python stdio path should expose it as a named tool. The generic passthrough can discover it without a Python code change.

Do not create a new Kotlin transport, dispatcher, registry, or build configuration for an ordinary tool. Keep `me.wenaco.burpmcp`, Java 21, and Montoya as `compileOnly`.

## 5. Documentation To Restore (Not Runtime Blockers)

These are useful project documents, but their absence does not prevent the current extension from serving tools. Create them only when the implementation is ready to document:

- `extension/docs/ARCHITECTURE.md`: Python-vs-Kotlin responsibilities, MCP client/server boundaries, extension lifecycle, transport modes, request flow, and security boundary.
- `extension/docs/EXTENSION-COMPAT.md`: tested Burp editions/versions, Montoya API version, Java runtime expectations, and which tools require Burp Professional. Mark untested combinations clearly.
- `extension/docs/SPEC-maturity.md`: implemented MCP methods/capabilities and explicitly deferred items. Current docs/source identify progress notifications, MCP resources, and prompts as not implemented; do not claim support until coded and tested.

Keep `extension/docs/CONNECTING.md` as the practical client setup guide. Avoid documenting protocol support as tested until a compatible client has connected successfully.

## 6. Definition of Done

For a first complete Python interface:

- `./gradlew test shadowJar` passes for the Kotlin extension.
- Python tests pass without Burp running.
- Python tool listing contains the expected 34 unique names, including `scan_results_workflow`.
- Each Kotlin-backed Python wrapper forwards to its exact Kotlin tool and matches the Kotlin input schema.
- A live local test confirms Python can connect to a loaded extension and list all 30 Kotlin tools.
- Optional bearer-token mode works without exposing the token in logs.
- A harmless live call succeeds; traffic-producing behavior is tested only against an authorized, in-scope lab.
- Setup documentation clearly says whether the user should connect directly to Burp over SSE or use the Python stdio server.

For a new custom tool, add its requirement, implementation, registration, tests, and documentation as one small vertical slice. Do not add tools merely to increase the count; add them to solve a concrete workflow you actually need.
