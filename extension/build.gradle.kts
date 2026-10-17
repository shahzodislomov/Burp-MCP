plugins {
    kotlin("jvm") version "2.0.21"
    kotlin("plugin.serialization") version "2.0.21"
    id("com.gradleup.shadow") version "8.3.5"
}

group = "me.wenaco.burpmcp"
version = "0.1.0-fork"

repositories {
    mavenCentral()
}

dependencies {
    // Burp provides the Montoya API at runtime -> compileOnly, never bundled.
    compileOnly("net.portswigger.burp.extensions:montoya-api:2025.5")
    // Our only bundled runtime dependency: JSON for the MCP/JSON-RPC layer.
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
    testImplementation(kotlin("test"))
    testImplementation("net.portswigger.burp.extensions:montoya-api:2025.5")
}

kotlin {
    jvmToolchain(21)
}

tasks.shadowJar {
    // This fat jar is what you load into Burp (Extensions > Add > Java).
    archiveBaseName.set("burp-mcp")
    archiveClassifier.set("")
    archiveVersion.set(project.version.toString())
    // Each Burp extension gets its own classloader, so bundling (not relocating)
    // kotlin-stdlib + kotlinx-serialization is safe.
    mergeServiceFiles()
}

// `./gradlew build` should produce the loadable fat jar.
tasks.named("build") { dependsOn(tasks.named("shadowJar")) }

tasks.test { useJUnitPlatform() }
