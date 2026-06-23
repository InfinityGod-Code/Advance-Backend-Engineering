# Multi-Module Architecture Guide

## Overview

This project is a **multi-module Maven project** consisting of 6 modules managed by a single root parent POM:

```
package-tracker-mono/          (root - pom packaging)
├── common-events/             (jar - shared event DTOs)
├── customer-service/          (jar - REST + Kafka)
├── delivery-service/          (jar - REST + Kafka)
├── notification-service/      (jar - REST + Kafka)
└── shipment-service/          (jar - REST + Kafka)
```

## Parent-Child POM Hierarchy

### How Spring Boot Multi-Module Is Structured

1. **Root POM** (`pom.xml`) acts as the single source of truth:
   - It inherits from `spring-boot-starter-parent` (the Spring Boot BOM), gaining all Spring Boot managed dependencies
   - Declares all modules via `<modules>`
   - Centralizes dependency versions via `<dependencyManagement>`
   - Centralizes plugin config via `<pluginManagement>`

2. **Each submodule POM** inherits from the **root POM**, NOT from `spring-boot-starter-parent`:
   ```xml
   <parent>
       <groupId>com.tracker</groupId>
       <artifactId>package-tracker-parent</artifactId>
       <version>1.0.0</version>
       <relativePath>../pom.xml</relativePath>
   </parent>
   ```
   This way, version management (Spring Boot, plugins, etc.) flows from root to submodules.

## Fixes Applied

### Root POM (`pom.xml`)
- Added `<parent>` referencing `spring-boot-starter-parent:4.1.0`
- Added `<properties>` with `java.version=21` and `spring-cloud.version`
- Added `<dependencyManagement>` to centralize all dependency versions
- Added `<pluginManagement>` with `spring-boot-maven-plugin` and `maven-compiler-plugin` (including Lombok annotation processor config)
- Kept all 5 modules declared under `<modules>`

### Submodule POMs (customer, delivery, notification, shipment, common-events)
- Changed `<parent>` from `spring-boot-starter-parent` to root POM
- Standardized `groupId` to `com.tracker` across all modules
- Fixed invalid dependencies: `spring-boot-starter-webmvc` → `spring-boot-starter-web`, `spring-boot-starter-webmvc-test` → `spring-boot-starter-test`
- Removed duplicate plugin configurations (now inherited from root)
- Removed `spring-cloud-dependencies` BOM from shipment-service (moved to root `<dependencyManagement>`)
- Removed boilerplate XML (empty `<description>`, `<url>`, `<licenses>`, `<developers>`, `<scm>`)

### Java Package Structure
- `delivery-service`: Moved main + test classes from `com.example.demo` to `com.tracker.delivery_service`
- `shipment-service`: Moved main + test classes from `com.example.demo` to `com.tracker.shipment_service`
- Old `com/example/` directories deleted

### Cleanup
- Removed duplicate `mvnw`, `mvnw.cmd`, `.mvn/` from all 4 submodules (wrapper kept only at root)
- Removed IDE files (`.idea/`, `.vscode/`, `.settings/`, `.project`, `.gitattributes`) and `HELP.md` from submodules

## How to Build

```bash
# Compile all modules
./mvnw clean compile

# Run all tests
./mvnw clean test

# Build a single module with its dependencies
./mvnw -pl customer-service -am clean package

# Package all modules (skipping tests)
./mvnw clean package -DskipTests
```

## Docker & Docker Compose

Each service has its own `Dockerfile` using multi-stage builds:
1. **Build stage**: `maven:3.9-eclipse-temurin-21` compiles the specific module (uses `-pl {module} -am` to also build dependencies)
2. **Runtime stage**: `eclipse-temurin:21-jre` runs the JAR on port 8080

The root `docker-compose.yml` orchestrates:
- **Zookeeper** (port 2181) — Kafka coordination service
- **Kafka** (port 9092) — message broker
- **4 services** on ports 8081-8084 with `SPRING_KAFKA_BOOTSTRAP_SERVERS=kafka:9092`

```bash
# Build and start all services
docker compose up --build

# Start a single service
docker compose up customer-service
```

## Key Design Principles

- **Single source of truth**: Spring Boot version, Java version, and all dependency versions are defined once in the root POM
- **Consistent groupId**: `com.tracker` for every module
- **Consistent package naming**: `com.tracker.{service_name}` using underscore notation
- **DRY plugin config**: Plugin configuration lives in root `<pluginManagement>`, submodules inherit without repeating
- **`common-events` module**: Meant for shared Kafka event DTOs — services can add a dependency to it if needed
