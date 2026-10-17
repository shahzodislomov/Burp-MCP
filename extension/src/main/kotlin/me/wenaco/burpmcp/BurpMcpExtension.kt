package me.wenaco.burpmcp

import burp.api.montoya.BurpExtension
import burp.api.montoya.MontoyaApi
import me.wenaco.burpmcp.collab.CollaboratorHolder
import me.wenaco.burpmcp.mcp.McpServer
import me.wenaco.burpmcp.mcp.ToolRegistry
import me.wenaco.burpmcp.safety.RoeGuard
import me.wenaco.burpmcp.scan.ScanRegistry
import me.wenaco.burpmcp.ui.BurpMcpTab
import me.wenaco.burpmcp.tools.CollaboratorInteractionsTool
import me.wenaco.burpmcp.tools.CollaboratorPayloadTool
import me.wenaco.burpmcp.tools.FuzzTool
import me.wenaco.burpmcp.tools.GetWebsocketHistoryTool
import me.wenaco.burpmcp.tools.SendToComparerTool
import me.wenaco.burpmcp.tools.ExportBurpConfigTool
import me.wenaco.burpmcp.tools.ImportBurpConfigTool
import me.wenaco.burpmcp.tools.RandomStringTool
import me.wenaco.burpmcp.tools.SendToIntruderTool
import me.wenaco.burpmcp.tools.SendToOrganizerTool
import me.wenaco.burpmcp.tools.SendToRepeaterTool
import me.wenaco.burpmcp.tools.SetTaskEngineTool
import me.wenaco.burpmcp.tools.TransformTool
import me.wenaco.burpmcp.tools.GenerateReportTool
import me.wenaco.burpmcp.tools.GetProxyEntryTool
import me.wenaco.burpmcp.tools.GetProxyHistoryTool
import me.wenaco.burpmcp.tools.GetScannerIssuesTool
import me.wenaco.burpmcp.tools.ImportBCheckTool
import me.wenaco.burpmcp.tools.ScanStatusTool
import me.wenaco.burpmcp.tools.ScopeAddTool
import me.wenaco.burpmcp.tools.ScopeCheckTool
import me.wenaco.burpmcp.tools.ScopeRemoveTool
import me.wenaco.burpmcp.tools.SendHttpRequestTool
import me.wenaco.burpmcp.tools.SendHttpRequestsTool
import me.wenaco.burpmcp.tools.SetInterceptTool
import me.wenaco.burpmcp.tools.SitemapQueryTool
import me.wenaco.burpmcp.tools.PassiveScanTool
import me.wenaco.burpmcp.tools.StartActiveScanTool
import me.wenaco.burpmcp.tools.StartCrawlTool
import me.wenaco.burpmcp.tools.StopScanTool

/**
 * BurpMCP — a Montoya-based MCP server for Burp Suite Pro.
 *
 * Discovered by Burp via META-INF/services/burp.api.montoya.BurpExtension.
 * System properties:
 *   -Dburpmcp.host / -Dburpmcp.port      bind address (default 127.0.0.1:9262)
 *   -Dburpmcp.token                    require Authorization: Bearer <token>
 *   -Dburpmcp.allowOutOfScope=true     disable the ROE scope guard (lab only)
 */
class BurpMcpExtension : BurpExtension {

    private var server: McpServer? = null

    override fun initialize(api: MontoyaApi) {
        api.extension().setName("BurpMCP")
        val log = api.logging()
        log.logToOutput("BurpMCP v0.1.0-fork loading...")

        val host = System.getProperty("burpmcp.host") ?: "127.0.0.1"
        val port = (System.getProperty("burpmcp.port") ?: "9262").toIntOrNull() ?: 9262
        val token = System.getProperty("burpmcp.token")?.takeIf { it.isNotBlank() }
        val allowOutOfScope = System.getProperty("burpmcp.allowOutOfScope")?.toBoolean() ?: false

        val scans = ScanRegistry()
        val roe = RoeGuard(api)
        val collab = CollaboratorHolder(api, log)

        val registry = ToolRegistry()
            // v0.1 core
            .register(SendHttpRequestTool(api, roe))
            .register(SendHttpRequestsTool(api, roe))
            .register(GetProxyHistoryTool(api))
            .register(GetProxyEntryTool(api))
            // v0.3 native fuzzer (ROE-guarded)
            .register(FuzzTool(api, roe))
            // v0.2 scanner loop (active ones ROE-guarded)
            .register(StartActiveScanTool(api, scans, roe))
            .register(PassiveScanTool(api, scans, roe))
            .register(StartCrawlTool(api, scans, roe))
            .register(ScanStatusTool(scans))
            .register(StopScanTool(scans))
            .register(GetScannerIssuesTool(api, scans))
            .register(GenerateReportTool(api, scans))
            // v0.4 visibility & control
            .register(ScopeCheckTool(api))
            .register(ScopeAddTool(api))
            .register(SitemapQueryTool(api))
            .register(CollaboratorPayloadTool(collab))
            .register(CollaboratorInteractionsTool(collab))
            // v0.5 control + bchecks
            .register(ScopeRemoveTool(api))
            .register(SetInterceptTool(api))
            .register(ImportBCheckTool(api))
            // v0.6 send-to, utilities, config, task engine
            .register(SendToRepeaterTool(api))
            .register(SendToIntruderTool(api))
            .register(SendToOrganizerTool(api))
            .register(TransformTool(api))
            .register(RandomStringTool(api))
            .register(SetTaskEngineTool(api))
            .register(ExportBurpConfigTool(api))
            .register(ImportBurpConfigTool(api))
            // v0.7 niche
            .register(GetWebsocketHistoryTool(api))
            .register(SendToComparerTool(api))

        val mcp = McpServer(host, port, registry, log, serverVersion = "1.1.3", authToken = token)
        mcp.start()
        server = mcp

        val url = "http://$host:$port/"
        val auth = if (token != null) "token-protected" else "no-auth (loopback)"
        runCatching {
            api.userInterface().registerSuiteTab("BurpMCP", BurpMcpTab.build(url, auth, allowOutOfScope, registry))
        }.onFailure { log.logToError("[BurpMCP] suite tab unavailable: ${it.message}") }

        api.extension().registerUnloadingHandler {
            log.logToOutput("BurpMCP unloading...")
            server?.stop()
        }

        log.logToOutput("BurpMCP ready -> $url  (${registry.size()} tools, $auth)")
    }
}
