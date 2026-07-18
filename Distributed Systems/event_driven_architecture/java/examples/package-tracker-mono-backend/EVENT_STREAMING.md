# Event Streaming — API Gateway + SSE

This document explains how real-time events from all microservices are streamed to clients through a single API Gateway endpoint using Server-Sent Events (SSE), and how the Retry + Dead Letter Topic (DLT) pattern protects the event pipeline.

## Architecture

```
                                   ┌─────────────────┐
                                   │  Eureka Server   │
                                   │  (port 8761)     │
                                   └────────┬────────┘
                                            │ registers
                               ┌────────────┼──────────────────┐
                               ▼            ▼                   ▼
Client ──→ Gateway (port 8086) ──(lb://)──→ notification-service
                               │            │
                               │            ├── Kafka: order-events ──→ retry-0/1/2 → dlt
                               │            ├── Kafka: shipment-events ──→ retry-0/1/2 → dlt
                               │            └── Kafka: delivery-events ──→ retry-0/1/2 → dlt
                               │            └── SSE: /api/v1/events/stream
                               │
                               ├──(lb://)──→ customer-service (produces order-events)
                               ├──(lb://)──→ shipment-service (consumes order-events → produces shipment-events)
                               │                               └── retry-0/1/2 → dlt
                               └──(lb://)──→ delivery-service (consumes shipment-events → produces delivery-events)
                                                               └── retry-0/1/2 → dlt
```

All services register with Eureka. The Gateway resolves targets via `lb://<service-id>` using Eureka + Spring Cloud LoadBalancer.

### Services involved

| Service | Port | Registers with Eureka | Role |
|---------|------|-----------------------|------|
| `eureka-server` | 8761 | — (server) | Service registry & discovery |
| `gateway-service` | 8086 | ✓ | Single entry point, resolves targets via Eureka |
| `notification-service` | 8083 | ✓ | Kafka consumers + SSE emitter registry + broadcast |
| `delivery-service` | 8082 | ✓ | Produces `DeliveryStartedEvent` to `delivery-events` |

## Event Topics

| Topic | Produced By | Consumed By (notifications) | Retry Protection | DLT |
|-------|------------|------------------------------|------------------|-----|
| `order-events` | customer-service | notification-service | ✓ retry-0/1/2 | ✓ order-events-dlt |
| `shipment-events` | shipment-service | notification-service, delivery-service | ✓ retry-0/1/2 | ✓ shipment-events-dlt |
| `delivery-events` | delivery-service | notification-service | ✓ retry-0/1/2 | ✓ delivery-events-dlt |
| `dead-letter-events` | all services | — (centralized DLT monitoring) | — | — |

## SSE Endpoint

### Connect

```
GET http://localhost:8086/api/v1/events/stream
```

The gateway proxies this to `notification-service:8080/api/v1/events/stream`.

### Event Types

Once connected, the server pushes events with typed SSE event names:

```
event: OrderCreated
data: {"orderId":"ORD-XXX","customerId":"1","totalAmount":49.99","timestamp":...}

event: ShipmentStarted
data: {"orderId":"ORD-XXX","shipmentId":"SHP-XXX","customerId":"1","timestamp":...}

event: DeliveryStarted
data: {"deliveryId":"DEL-XXX","orderId":"ORD-XXX","shipmentId":"SHP-XXX","customerId":"1","timestamp":...}
```

### Client Example (JavaScript)

```javascript
const source = new EventSource('http://localhost:8086/api/v1/events/stream');

source.addEventListener('OrderCreated', (e) => {
    const event = JSON.parse(e.data);
    console.log('Order created:', event.orderId);
});

source.addEventListener('ShipmentStarted', (e) => {
    const event = JSON.parse(e.data);
    console.log('Shipment started:', event.shipmentId);
});

source.addEventListener('DeliveryStarted', (e) => {
    const event = JSON.parse(e.data);
    console.log('Delivery started:', event.deliveryId);
});

source.onerror = () => {
    console.log('SSE connection lost, reconnecting...');
};
```

### Client Example (curl)

```bash
curl -N http://localhost:8086/api/v1/events/stream
```

This keeps the connection open and prints each event as it arrives.

## Event Flow (End to End)

```
1. customer-service creates order
   → publishes OrderCreatedEvent to order-events
   → notification-service consumes, broadcasts SSE "OrderCreated"
   
2. shipment-service consumes OrderCreatedEvent
   → creates shipment, publishes ShipmentStartedEvent to shipment-events
   → notification-service consumes, broadcasts SSE "ShipmentStarted"
   
3. delivery-service consumes ShipmentStartedEvent
   → assigns delivery, publishes DeliveryStartedEvent to delivery-events
   → notification-service consumes, broadcasts SSE "DeliveryStarted"
```

### Failure Scenario (DB Down)

```
1. customer-service creates order
   → publishes OrderCreatedEvent to order-events

2. shipment-service tries to consume OrderCreatedEvent
   → DB is down → DataAccessException thrown
   → @RetryableTopic forwards to order-events-retry-0
   → After 1s, retry → still fails → order-events-retry-1
   → After 2s, retry → still fails → order-events-retry-2
   → After 4s, retry → still fails → order-events-dlt
   → @DltHandler logs error, sends DeadLetterEvent to dead-letter-events

3. DB comes back online
   → admin re-publishes from order-events-dlt via AKHQ
   → shipment-service successfully processes the message
   → event chain continues normally
```

## Gateway Routes

The `gateway-service` uses Spring Cloud Gateway with routes:

| Route | Target |
|-------|--------|
| `/api/v1/events/stream/**` | `lb://notification-service` |
| `/api/v1/users/**` | `lb://customer-service` |
| `/api/v1/orders/**` | `lb://customer-service` |
| `/api/v1/shipments/**` | `lb://shipment-service` |
| `/api/v1/deliveries/**` | `lb://delivery-service` |

## Testing

### 1. Connect to SSE

```bash
curl -N http://localhost:8086/api/v1/events/stream
```

Keep this terminal open.

### 2. Create a user

```bash
curl -s -X POST http://localhost:8081/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@test.com","phone":"555-0000","address":{"street":"1 St","city":"City","state":"ST","zip":"00000"}}'
```

### 3. Create an order

```bash
curl -s -X POST http://localhost:8081/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"userId":1,"totalAmount":99.99}'
```

### 4. Watch the SSE stream

You will see three events in order:
```
event: OrderCreated
event: ShipmentStarted
event: DeliveryStarted
```

### 5. Test DLT (simulate failure)

```bash
# Stop a database to trigger retry + DLT
docker compose stop shipment-db

# Create an order — it will fail in shipment-service
curl -s -X POST http://localhost:8086/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"userId":1,"totalAmount":99.99}'

# Watch shipment-service logs
docker compose logs -f shipment-service
# Look for retry pattern → DLT

# Check AKHQ at http://localhost:8085
# Topics → order-events-dlt → 1 message
# Topics → dead-letter-events → 1 DeadLetterEvent
```

## Troubleshooting

**SSE connection fails:**
- Ensure all services are running: `docker compose ps`
- Check gateway logs: `docker compose logs gateway-service`
- Check notification-service logs: `docker compose logs notification-service`

**Events not appearing:**
- Verify the full event chain worked: check logs of customer-service → shipment-service → delivery-service → notification-service
- Check AKHQ at http://localhost:8085 for topic messages and consumer group lag

**Messages going to DLT unexpectedly:**
- Check the error message in the DeadLetterEvent
- Common causes: DB not reachable, schema mismatch, invalid event data
- Re-publish from DLT via AKHQ after fixing the issue

**Gateway not routing:**
- Verify `gateway-service` can reach `notification-service`: `docker compose exec gateway-service curl -s http://notification-service:8080/api/v1/events/stream`
