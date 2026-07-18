# Running the Package Tracker Backend

## Prerequisites

- **Java 21** (Eclipse Temurin recommended)
- **Docker** & **Docker Compose** (for Docker mode)
- **Maven** — the project includes a Maven wrapper (`./mvnw`) at the root
- **PostgreSQL 16** + **Kafka** (only needed for local non-Docker mode)

## Running with Docker (Recommended)

### 1. Build all JARs

```bash
./mvnw clean package -DskipTests
```

### 2. Start everything

```bash
docker compose up --build
```

This starts all services, databases, Kafka, and the AKHQ Kafka UI.

### Services & Ports

| Service             | Internal Port | Exposed Port |
|---------------------|---------------|--------------|
| Eureka Server       | 8761          | 8761         |
| Gateway             | 8080          | 8086         |
| Customer Service    | 8080          | 8081         |
| Delivery Service    | 8080          | 8082         |
| Notification Service| 8080          | 8083         |
| Shipment Service    | 8080          | 8084         |
| AKHQ (Kafka UI)     | 8080          | 8085         |
| Kafka               | 9092          | 9092         |

### 3. Stop

```bash
docker compose down
```

To also remove database volumes:

```bash
docker compose down -v
```

### Eureka Dashboard

Once running, access the Eureka dashboard at [http://localhost:8761](http://localhost:8761) to see all registered services.

---

## Running Without Docker (Local Development)

### 1. Start Infrastructure

**PostgreSQL** — create 4 databases:

```bash
createdb -p 5432 customerdb
createdb -p 5433 shipmentdb
createdb -p 5434 deliverydb
createdb -p 5435 notificationdb
```

Or run PostgreSQL via Docker for just the databases:

```bash
docker compose up -d customer-db shipment-db delivery-db notification-db
```

**Kafka** — start on `localhost:9092` (e.g. via `docker compose up -d kafka` or a local install).

### 2. Fix Kafka Hostname in Properties

> `delivery-service/src/main/resources/application.properties` and
> `notification-service/src/main/resources/application.properties`
> reference `kafka:9092` (the Docker network hostname).
> For local development, change it to `localhost:9092`.

```properties
spring.kafka.bootstrap-servers=localhost:9092
```

### 3. Start Each Service

Open separate terminals and run each service:

```bash
# Terminal 1 — Customer Service (port 8081)
./mvnw -pl customer-service -am spring-boot:run

# Terminal 2 — Shipment Service (port 8084)
./mvnw -pl shipment-service -am spring-boot:run

# Terminal 3 — Delivery Service (port 8082)
./mvnw -pl delivery-service -am spring-boot:run

# Terminal 4 — Notification Service (port 8083)
./mvnw -pl notification-service -am spring-boot:run

# Terminal 5 — Gateway (port 8086)
./mvnw -pl gateway-service -am spring-boot:run
```

Alternatively, package and run JARs:

```bash
./mvnw clean package -DskipTests
java -jar gateway-service/target/*.jar
# ... repeat for each service
```

---

## Service Port Map & Gateway Routes

All services register with **Eureka Server** (port 8761). The Gateway uses `lb://` (load-balanced) URIs resolved via Eureka instead of hardcoded hostnames.

| Gateway Path                       | Target Service       | Eureka Service ID     |
|------------------------------------|----------------------|-----------------------|
| `/api/v1/users/**`                 | Customer Service     | `customer-service`    |
| `/api/v1/orders/**`                | Customer Service     | `customer-service`    |
| `/api/v1/shipments/**`             | Shipment Service     | `shipment-service`    |
| `/api/v1/deliveries/**`            | Delivery Service     | `delivery-service`    |
| `/api/v1/events/stream`            | Notification Service | `notification-service`|

All external traffic goes through the Gateway on **port 8086**.

---

## Verifying the Application

### 1. Connect to the SSE event stream

```bash
curl -N http://localhost:8086/api/v1/events/stream
```

Keep this terminal open.

### 2. Create a user

```bash
curl -s -X POST http://localhost:8086/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@test.com","phone":"555-0000","address":{"street":"1 St","city":"City","state":"ST","zip":"00000"}}'
```

### 3. Create an order

```bash
curl -s -X POST http://localhost:8086/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"userId":1,"totalAmount":99.99}'
```

### 4. Watch events cascade

You should see three SSE events in order:

```
event: OrderCreated
event: ShipmentStarted
event: DeliveryStarted
```

---

## Monitoring with AKHQ

AKHQ is available at [http://localhost:8085](http://localhost:8085). Use it to:

- **View topics**: Check all Kafka topics including retry and DLT topics
- **Inspect messages**: Browse messages in any topic including `dead-letter-events`
- **Monitor consumer groups**: Check consumer lag for each service
- **Replay dead letters**: Re-publish messages from DLT topics back to original topics

### Topics Created After Running

Once the application runs and produces/consumes messages, the following topics will exist:

| Topic | Purpose |
|-------|---------|
| `order-events` | Main order events (produced by customer-service) |
| `order-events-retry-0` | First retry for order events |
| `order-events-retry-1` | Second retry for order events |
| `order-events-retry-2` | Third retry for order events |
| `order-events-dlt` | Dead letter topic for order events |
| `shipment-events` | Main shipment events (produced by shipment-service) |
| `shipment-events-retry-0` | First retry for shipment events |
| `shipment-events-retry-1` | Second retry for shipment events |
| `shipment-events-retry-2` | Third retry for shipment events |
| `shipment-events-dlt` | Dead letter topic for shipment events |
| `delivery-events` | Main delivery events (produced by delivery-service) |
| `delivery-events-retry-0` | First retry for delivery events |
| `delivery-events-retry-1` | Second retry for delivery events |
| `delivery-events-retry-2` | Third retry for delivery events |
| `delivery-events-dlt` | Dead letter topic for delivery events |
| `dead-letter-events` | Centralized dead letter event log (all services) |

---

## Testing the Retry + DLT Pattern

### Test: Transient Failure (DB Down)

```bash
# 1. Start everything
docker compose up --build

# 2. Connect SSE to monitor events
curl -N http://localhost:8086/api/v1/events/stream &

# 3. Simulate shipment-db failure
docker compose stop shipment-db

# 4. Create an order (will fail in shipment-service)
curl -s -X POST http://localhost:8086/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"userId":1,"totalAmount":99.99}'

# 5. Watch the retry pattern in shipment-service logs
docker compose logs -f shipment-service
# Expected: error → retry-0 → retry-1 → retry-2 → DLT

# 6. Verify in AKHQ at http://localhost:8085
# Topics → order-events-dlt → should have 1 message
# Topics → dead-letter-events → should have 1 DeadLetterEvent

# 7. Restart DB and replay
docker compose start shipment-db
# Wait for DB health check to pass
# Re-publish the message from order-events-dlt via AKHQ
```

---

## Troubleshooting

| Problem                          | Check                                                                  |
|----------------------------------|------------------------------------------------------------------------|
| Services won't start             | Java 21 is required — verify with `java -version`                      |
| Docker build fails               | Ensure JARs exist: `./mvnw clean package -DskipTests` before `docker compose up --build` |
| SSE connection fails             | Run `docker compose ps` to verify all services are up                  |
| Events not appearing             | Check logs of each service: `docker compose logs <service-name>`       |
| Kafka connection refused         | Ensure Kafka is running on port 9092                                   |
| AKHQ shows no topics            | Access AKHQ at http://localhost:8085 to inspect topics and consumer groups |
| Port conflicts                   | Change exposed ports in `docker-compose.yml` if ports 8081-8086 are in use |
| `kafka:9092` connection error   | In local mode, update `spring.kafka.bootstrap-servers` to `localhost:9092` |
| Messages going to DLT            | Check the DeadLetterEvent in `dead-letter-events` topic via AKHQ for the error reason |
| Retry topics not appearing       | They are auto-created when a message first fails. Trigger a failure to create them. |
