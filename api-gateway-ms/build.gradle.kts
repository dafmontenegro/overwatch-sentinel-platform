import com.github.jengelman.gradle.plugins.shadow.tasks.ShadowJar
import org.gradle.api.tasks.testing.logging.TestLogEvent.*

plugins {
    java
    application
    id("com.github.johnrengelman.shadow") version "8.1.1"
}

group = "com.unal"
version = "1.0.0-SNAPSHOT"

repositories {
    mavenCentral()
}

val vertxVersion = "4.5.1"
val junitJupiterVersion = "5.9.1"

val mainVerticleName = "com.unal.api_gateway_ms.MainVerticle"

application {
    mainClass.set("io.vertx.core.Launcher")
}

dependencies {
    implementation(platform("io.vertx:vertx-stack-depchain:$vertxVersion"))
    implementation("io.vertx:vertx-web")
    implementation("io.vertx:vertx-core")
    implementation("io.vertx:vertx-web-client")
    implementation("io.vertx:vertx-web-openapi")
    implementation("io.vertx:vertx-web-api-contract")
    implementation("io.vertx:vertx-redis-client")
    testImplementation("io.vertx:vertx-junit5")
    testImplementation("org.junit.jupiter:junit-jupiter:$junitJupiterVersion")
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

tasks.withType<ShadowJar> {
    archiveBaseName.set("api-gateway-ms")
    archiveClassifier.set("fat")  // Esto genera el -fat.jar
    archiveVersion.set("")
    manifest {
        attributes(mapOf(
            "Main-Class" to "io.vertx.core.Launcher",
            "Main-Verticle" to "com.unal.api_gateway_ms.MainVerticle"
        ))
    }
    mergeServiceFiles()
}

tasks.withType<Test> {
    useJUnitPlatform()
    testLogging {
        events = setOf(PASSED, SKIPPED, FAILED)
    }
}