# Event Streaming — API Gateway + SSE

This document explains how real-time events from all microservices are streamed to clients through a single API Gateway endpoint using Server-Sent Events (SSE).

## Architecture

```
Client ──→ Gateway (port 8086) ──proxy──→ notification-service (port 8080)
                                              │
                                              ├── Kafka: order-events
                                              ├── Kafka: shipment-events
                                              └── Kafka: delivery-events
                                              └── SSE: /api/v1/events/stream
```

### Services involved

| Service | Port | Role |
|---------|------|------|
| `gateway-service` | 8086 | Single entry point, proxies SSE to notification-service |
| `notification-service` | 8083 | Kafka consumers + SSE emitter registry + broadcast |
| `delivery-service` | 8082 | Produces `DeliveryStartedEvent` to `delivery-events` |

## Event Topics

| Topic | Produced By | Consumed By (notifications) |
|-------|------------|------------------------------|
| `order-events` | customer-service | notification-service |
| `shipment-events` | shipment-service | notification-service, delivery-service |
| `delivery-events` | delivery-service | notification-service |

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
data: {"orderId":"ORD-XXX","customerId":"1","totalAmount":49.99,"timestamp":...}

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

## Gateway Routes

The `gateway-service` uses Spring Cloud Gateway with a single route:

| Route | Target |
|-------|--------|
| `/api/v1/events/stream/**` | `http://notification-service:8080` |

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

## Troubleshooting

**SSE connection fails:**
- Ensure all services are running: `docker compose ps`
- Check gateway logs: `docker compose logs gateway-service`
- Check notification-service logs: `docker compose logs notification-service`

**Events not appearing:**
- Verify the full event chain worked: check logs of customer-service → shipment-service → delivery-service → notification-service
- Check AKHQ at http://localhost:8085 for topic messages and consumer group lag

**Gateway not routing:**
- Verify `gateway-service` can reach `notification-service`: `docker compose exec gateway-service curl -s http://notification-service:8080/api/v1/events/stream`
