package me.wenaco.burpmcp.collab

import burp.api.montoya.MontoyaApi
import burp.api.montoya.collaborator.CollaboratorClient
import burp.api.montoya.logging.Logging

/** Holds a single Collaborator client so payloads and polled interactions correlate. */
class CollaboratorHolder(api: MontoyaApi, log: Logging) {
    val client: CollaboratorClient? = runCatching { api.collaborator().createClient() }
        .onFailure { log.logToError("[BurpMCP] Collaborator unavailable (Pro only?): ${it.message}") }
        .getOrNull()
}
