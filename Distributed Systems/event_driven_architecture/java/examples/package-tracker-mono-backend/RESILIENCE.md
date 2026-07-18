# Resilience: Circuit Breaker + Retry + Dead Letter Topic (DLT)

This system uses two complementary resilience patterns at different layers of the architecture:

| Layer | Pattern | Protection Against |
|-------|---------|-------------------|
| **API Gateway** (edge) | **Circuit Breaker** | Downstream service outages — fail fast with 503 instead of hanging |
| **Kafka Consumers** (internal) | **Retry + DLT** | Transient failures (DB down, network) — retry with backoff, then quarantine in DLT |

---

# Circuit Breaker Pattern (Gateway)

## Why Only at the Gateway?

The gateway is the only place where **synchronous HTTP calls** happen. When a downstream service is down:

- **Without circuit breaker**: the gateway hangs on the connection until timeout, exhausting the Netty connection pool and making the gateway itself vulnerable
- **With circuit breaker**: after N consecutive failures, the circuit opens and the gateway immediately returns a structured 503 response without even attempting the connection

**Kafka producers** don't need circuit breakers because `KafkaTemplate.send()` is non-blocking and Kafka's internal retries handle broker failures. **JPA repositories** don't need them because connection pool timeouts already fail fast, and the Retry + DLT pattern on the consumer side handles DB failures there.

## Architecture

```
                        ┌───────────────┐
Client ──→ Gateway ────→ Circuit Breaker ────→ customer-service
                        │     │
                        │     └── CLOSED (normal): passthrough
                        │     └── OPEN (failing): return 503 fallback
                        │     └── HALF_OPEN (probing): allow 1, then decide
                        │
                        ├── Circuit Breaker ────→ shipment-service
                        │
                        └── Circuit Breaker ────→ delivery-service
                        
    (SSE stream → notification-service — no circuit breaker, long-lived connection)
```

## Implementation

### 1. Dependency

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>
</dependency>
```

### 2. Route Configuration with Circuit Breaker (GatewayServiceApplication.java)

Each HTTP route (except SSE) wraps in a `circuitBreaker` filter with a named instance and a fallback URI:

```java
.route("customer-service", r -> r
    .path("/api/v1/users/**", "/api/v1/orders/**")
    .filters(f -> f.circuitBreaker(config -> config
            .setName("customerServiceCB")
            .setFallbackUri("forward:/fallback/customer-service")))
    .uri("lb://customer-service"))
```

The SSE route for `notification-service` is intentionally excluded — SSE connections are long-lived and don't benefit from circuit breaking.

### 3. Fallback Controller (FallbackController.java)

```java
@RestController
public class FallbackController {

    private static final Logger log = LoggerFactory.getLogger(FallbackController.class);

    @GetMapping("/fallback/customer-service")
    public Mono<Map<String, Object>> customerServiceFallback() {
        log.warn("Circuit breaker triggered for customer-service — returning 503 fallback");
        return Mono.just(Map.of(
                "status", 503,
                "error", "Service Unavailable",
                "message", "customer-service is temporarily unavailable. Please try again later."
        ));
    }
    // ... shipment-service, delivery-service
}
```

### 4. Resilience4J Configuration (application.yml)

```yaml
resilience4j:
  circuitbreaker:
    configs:
      default:
        sliding-window-size: 10
        minimum-number-of-calls: 5
        failure-rate-threshold: 50
        wait-duration-in-open-state: 30s
        permitted-number-of-calls-in-half-open-state: 3
        writable-stack-trace-enabled: true
```

### Configuration Breakdown

| Setting | Value | Meaning |
|---------|-------|---------|
| `sliding-window-size` | 10 | Count last 10 calls to evaluate health |
| `minimum-number-of-calls` | 5 | Don't trip until at least 5 calls recorded |
| `failure-rate-threshold` | 50 | Trip when ≥50% of calls fail |
| `wait-duration-in-open-state` | 30s | Stay OPEN for 30s before trying HALF_OPEN |
| `permitted-number-of-calls-in-half-open-state` | 3 | In HALF_OPEN, allow 3 probe calls before deciding |

## Circuit Breaker States

```
                    ┌──────────┐
         ┌─────────→│  CLOSED  │←──────── normal operation
         │          └─────┬────┘
         │                │ failure rate > 50%
         │                ▼
         │          ┌──────────┐
         │          │   OPEN   │────────── requests fail immediately with 503
         │          └─────┬────┘
         │                │ 30s timeout
         │                ▼
         │          ┌──────────┐
         │          │ HALF_OPEN│────────── probe: 3 requests pass through
         │          └─────┬────┘
         │                │
         ├── success ────→┤
         │                │ failure again
         └────────────────┘
```

## Testing the Circuit Breaker

### Manual End-to-End Test

```bash
# 1. Start everything
docker compose up --build

# 2. Stop a service to trigger circuit breaker
docker compose stop customer-service

# 3. Make several requests to trigger CB (5 failures = minimum threshold)
for i in $(seq 1 6); do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8086/api/v1/users
done

# Expected output:
# 500 (first few — before circuit opens)
# 503 (after circuit opens — fast failure)

# 4. Check gateway logs
docker compose logs gateway-service
# Expected:
# "Circuit breaker triggered for customer-service — returning 503 fallback"

# 5. Restart the service
docker compose start customer-service

# 6. Wait 30s (HALF_OPEN timeout), then request again — should recover
sleep 30
curl -s -w "\n%{http_code}" http://localhost:8086/api/v1/users/1
# Expected: 200 + user data (circuit closed again)
```

### Check Circuit Breaker State via Actuator

```bash
# If actuator is enabled, you can check CB state:
curl -s http://localhost:8086/actuator/health | jq
curl -s http://localhost:8086/actuator/circuitbreakers | jq
```

### Monitoring Logs

Each circuit breaker trip produces a structured log entry:
```
WARN  [FallbackController] Circuit breaker triggered for customer-service — returning 503 fallback
```

---

# Retry + Dead Letter Topic (DLT) Pattern

## Overview

This document explains the Retry + DLT (Dead Letter Topic) pattern implemented across all Kafka consumers in the package-tracker system. This pattern ensures that transient failures (database outages, network partitions) don't cause permanent message loss, while poison messages are isolated for manual inspection and replay.

## Architecture

```
                    ┌──────────────────────────────────┐
                    │         Original Topic            │
                    │    e.g. "order-events"            │
                    └──────────┬───────────────────────┘
                               │ consume
                    ┌──────────▼───────────────────────┐
                    │   @KafkaListener + @RetryableTopic │
                    │         consumer method           │
                    └──────────┬───────────────────────┘
                         ┌─────┴─────┐
                         │  Success? │
                         └─────┬─────┘
                    ┌──────────┴──────────┐
                    ▼                     ▼
              ack & done            ┌─────────────────────┐
                                    │ Is exception in     │
                                    │ `include` list?     │
                                    └──────────┬──────────┘
                                    ┌──────────┴──────────┐
                                    ▼                     ▼
                            ┌──────────────┐      ┌──────────────┐
                            │  Retry Topic  │      │   DLT Topic   │
                            │  {topic}-     │      │  {topic}-dlt  │
                            │  retry-{n}    │      └──────┬───────┘
                            └──────┬───────┘             │
                                   │ retry               │
                            ┌──────▼───────┐     ┌──────▼───────┐
                            │ Still fails  │     │ @DltHandler  │
                            │ after N      │     │ log + send   │
                            │ attempts?    │     │ DeadLetter-  │
                            └──────┬───────┘     │ Event        │
                                   │ yes         └──────────────┘
                                   ▼
                            ┌──────────────┐
                            │  DLT Topic    │
                            │  {topic}-dlt  │
                            └──────────────┘
```

## How It Works

### 1. `@RetryableTopic` Annotation

Every Kafka consumer method is annotated with `@RetryableTopic`. This annotation:

- Intercepts exceptions thrown by the consumer
- On success: passes through normally, message is acknowledged
- On transient failure (`DataAccessException`, `TimeoutException`): forwards the message to a retry topic with exponential backoff
- On non-transient failure (exceptions NOT in the `include` list): immediately routes to DLT

**Configuration (applied to every consumer):**

```java
@RetryableTopic(
    attempts = "4",                              // 1 original + 3 retries
    backOff = @BackOff(delay = 1000, multiplier = 2.0),  // 1s, 2s, 4s
    autoCreateTopics = "true",                    // auto-create retry/DLT topics
    dltTopicSuffix = "-dlt",                     // suffix for DLT topics
    retryTopicSuffix = "-retry-{attempt}",       // suffix for retry topics  
    include = {DataAccessException.class,        // retryable exceptions
              TimeoutException.class},
    kafkaTemplate = "retryableTopicKafkaTemplate" // template for forwarding
)
```

### 2. Retry Topics

For a topic named `order-events`, the retry infrastructure creates:

| Topic | Purpose |
|-------|---------|
| `order-events` | Original topic |
| `order-events-retry-0` | First retry (1s delay) |
| `order-events-retry-1` | Second retry (2s delay) |
| `order-events-retry-2` | Third retry (4s delay) |
| `order-events-dlt` | Dead letter topic (after 3 retries) |

Each retry topic is consumed by the same listener container, but with the configured backoff delay before consumption starts. This provides **non-blocking retry** — the consumer doesn't wait; it moves on to the next message while the failed message is deferred.

### 3. DLT Handler (`@DltHandler`)

When all retry attempts are exhausted, the message lands in the DLT. A `@DltHandler` method in the same class processes it:

```java
@DltHandler
public void onDltOrderCreated(
        @Payload OrderCreatedEvent event,
        @Header(KafkaHeaders.RECEIVED_KEY) String key,
        @Header(KafkaHeaders.RECEIVED_TOPIC) String originalTopic,
        @Header(KafkaHeaders.OFFSET) long offset,
        @Header(value = "x-retry-count", defaultValue = "0") int retryCount,
        Acknowledgment ack) {

    log.error("DLT received for orderId={} from topic={} after {} retries.",
            event.getOrderId(), originalTopic, retryCount);

    // Publish a DeadLetterEvent to the central dead-letter-events topic
    DeadLetterEvent dle = DeadLetterEvent.builder()
            .originalTopic(originalTopic)
            .originalKey(key)
            .originalValue(event.toString())
            .consumerGroup(consumerGroup)
            .serviceName(serviceName)
            .errorType("DataAccessException/TimeoutException")
            .errorMessage("Exhausted retries for orderId=" + event.getOrderId())
            .failedAt(System.currentTimeMillis())
            .retryCount(retryCount)
            .build();

    kafkaTemplate.send("dead-letter-events", dle.getOriginalKey(), dle);
    ack.acknowledge();
}
```

### 4. Dead Letter Event Schema

The centralized `dead-letter-events` topic uses the `DeadLetterEvent` DTO:

```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DeadLetterEvent {
    private String originalTopic;     // Topic where the message originally came from
    private String originalKey;       // Original message key
    private String originalValue;     // Original message value (toString)
    private String consumerGroup;     // Consumer group that failed
    private String serviceName;       // Service that failed
    private String errorType;         // Type of exception
    private String errorMessage;      // Error description
    private String stackTrace;        // Stack trace
    private long failedAt;            // Timestamp of failure
    private int retryCount;           // Number of retry attempts made
}
```

### 5. Retryable vs Non-Retryable Exceptions

| Exception Type | Behavior |
|----------------|----------|
| `DataAccessException` (DB down) | Retry 3 times with backoff → DLT |
| `TimeoutException` (Kafka timeout) | Retry 3 times with backoff → DLT |
| All others (incl. `JsonParseException`) | **Skip retry, direct to DLT** (poison message) |

This means poison messages (e.g., deserialization failures, invalid data) go directly to DLT without wasting retry attempts.

## Services Using This Pattern

| Service | Consumers | Topics Consumed | Retry Topics Created | DLT Topics Created |
|---------|-----------|-----------------|---------------------|-------------------|
| **shipment-service** | `OrderEventConsumer` | `order-events` | `order-events-retry-0/1/2` | `order-events-dlt` |
| **delivery-service** | `ShipmentEventListener` | `shipment-events` | `shipment-events-retry-0/1/2` | `shipment-events-dlt` |
| **notification-service** | `OrderEventListener` | `order-events` | `order-events-retry-0/1/2` | `order-events-dlt` |
| **notification-service** | `ShipmentEventListener` | `shipment-events` | `shipment-events-retry-0/1/2` | `shipment-events-dlt` |
| **notification-service** | `DeliveryEventListener` | `delivery-events` | `delivery-events-retry-0/1/2` | `delivery-events-dlt` |

## Message Flow Example

Here's what happens when a DB failure occurs in shipment-service while processing an order:

```
1. order-events: consumer reads message
2. shipmentService.createShipment() throws DataAccessException (DB down)
3. @RetryableTopic forwards to order-events-retry-0
4. After 1s delay, consumer reads from order-events-retry-0
5. DB still down → forwards to order-events-retry-1
6. After 2s delay, consumer reads from order-events-retry-1  
7. DB still down → forwards to order-events-retry-2
8. After 4s delay, consumer reads from order-events-retry-2
9. DB still down → forwards to order-events-dlt
10. @DltHandler fires: logs error, publishes DeadLetterEvent to dead-letter-events
11. Original consumer continues processing other messages uninterrupted
```

## Centralized Dead Letter Topic

All DLT handlers publish to a shared `dead-letter-events` topic. This provides a single place to monitor all failed messages across all services. A future admin service could consume this topic for alerting and dashboarding.

### Viewing Dead Letters in AKHQ

1. Open AKHQ at http://localhost:8085
2. Go to **Topics** → `dead-letter-events`
3. Browse messages to see all dead letter events across all services
4. Each message contains the original topic, key, error details, and service name

## Replaying Dead Letters

### Option 1: Manual Replay via AKHQ

1. Open AKHQ at http://localhost:8085
2. Navigate to the DLT topic (e.g., `order-events-dlt`)
3. View the failed message
4. Use AKHQ's "Produce" feature to re-publish the message to the original topic
5. Delete the DLT message if needed

### Option 2: Programmatic Replay (Future)

A dedicated `DeadLetterReplayController` can be added to each service:

```java
@RestController
@RequestMapping("/api/v1/admin/dead-letters")
public class DeadLetterReplayController {
    
    @PostMapping("/{id}/replay")
    public ResponseEntity<Void> replay(@PathVariable Long id) {
        // Re-publish dead letter to original topic
    }
    
    @PostMapping("/replay-all")
    public ResponseEntity<Void> replayAll() {
        // Re-publish all unreplayed dead letters
    }
    
    @GetMapping
    public ResponseEntity<List<DeadLetterEntity>> listAll() {
        // List all dead letters with status
    }
}
```

## Testing the Pattern

### Unit Test

```java
@Test
void consumer_shouldRetryThenDlt_whenDbThrows() {
    OrderCreatedEvent event = createTestOrderEvent();
    doThrow(new DataAccessException("DB down") {})
        .when(shipmentService).createShipment(event);
    
    assertThrows(DataAccessException.class, () -> {
        consumer.onOrderCreated(event, "key", 0, 1L, mock(Acknowledgment.class));
    });
    // @RetryableTopic intercepts the exception and forwards to retry topic
    // After all attempts exhausted, @DltHandler is invoked
}
```

### Integration Test with Embedded Kafka

```java
@SpringBootTest
@EmbeddedKafka(topics = "order-events", partitions = 1)
class OrderEventConsumerRetryTest {

    @Test
    void shouldLandInDltAfterRetries() {
        // Publish a message that will fail processing
        kafkaTemplate.send("order-events", "test-key", malformedEvent);
        
        // Wait for retries + DLT delivery
        Thread.sleep(15000);  // 1s + 2s + 4s + buffer
        
        // Verify message is in DLT
        Consumer<String, String> dltConsumer = createConsumer("order-events-dlt");
        ConsumerRecords<String, String> records = dltConsumer.poll(Duration.ofSeconds(5));
        assertThat(records.count()).isEqualTo(1);
    }
}
```

### Manual End-to-End Test

```bash
# 1. Start everything
docker compose up --build

# 2. Connect to SSE stream (monitor events)
curl -N http://localhost:8086/api/v1/events/stream &

# 3. Simulate a DB failure by stopping shipment-db
docker compose stop shipment-db

# 4. Create a user and order
curl -s -X POST http://localhost:8086/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"userId":1,"totalAmount":99.99}'

# 5. Watch shipment-service logs for retry pattern:
docker compose logs -f shipment-service
# Expected output:
# "Received OrderCreatedEvent: orderId=ORD-XXXX..."
# ! ERROR - DataAccessException thrown
# (message forwarded to order-events-retry-0)
# After 1s: same message consumed from retry-0
# After 2s: consumed from retry-1
# After 4s: consumed from retry-2
# "DLT received for orderId=ORD-XXXX from topic=order-events after 3 retries"

# 6. Verify DLT topics in AKHQ at http://localhost:8085
# Topics → order-events-dlt → should have 1 message
# Topics → dead-letter-events → should have 1 DeadLetterEvent

# 7. Restart DB and replay
docker compose start shipment-db
# Wait for DB to be healthy
# Manually re-publish from DLT via AKHQ
```

## Monitoring & Observability

### AKHQ Dashboard
- **URL**: http://localhost:8085
- **Topics tab**: see all retry and DLT topics with message counts
- **Consumer groups tab**: see consumer lag for each group

### Logs
Each DLT event produces a structured log entry:
```
ERROR [OrderEventConsumer] DLT received for orderId=ORD-XXXX from topic=order-events after 3 retries.
```

### Dead Letter Event Topic
The centralized `dead-letter-events` topic contains structured `DeadLetterEvent` objects that can be consumed by monitoring/alerting systems.
