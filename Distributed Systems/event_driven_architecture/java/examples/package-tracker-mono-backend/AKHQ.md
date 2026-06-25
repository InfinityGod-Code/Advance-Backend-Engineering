# AKHQ — Kafka Web UI

AKHQ (formerly KafkaHQ) is a web-based GUI for Apache Kafka. It lets you browse topics, view messages, inspect consumer groups, produce messages, and monitor cluster health — without writing any CLI commands.

## Access

| Service | URL |
|---------|-----|
| AKHQ | http://localhost:8085 |

## Prerequisites

All services must be running:

```bash
docker compose up -d
```

AKHQ connects to the `kafka` broker on port 9092 inside the Docker network.

## What You Can Do

- **Browse topics** — See all topics (`order-events`, `shipment-events`, `__consumer_offsets`, etc.)
- **View messages** — Click into a topic, then "Topic Data" to see the raw JSON messages produced by your services
- **Inspect consumer groups** — `shipment-service-group` and `notification-service-group` show current offset lag and partition assignments
- **Produce messages** — Send test messages directly from the UI to any topic
- **View cluster info** — Broker configuration, partition leadership, controller status

## Quick Tour

### 1. View Topics

Open http://localhost:8085 and click **Topics** in the left sidebar. You'll see all topics including:

- `order-events` — produced by `customer-service`, consumed by `shipment-service` and `notification-service`
- `shipment-events` — produced by `shipment-service`, consumed by `notification-service`
- Internal Kafka topics (`__consumer_offsets`, etc.)

### 2. Inspect Messages

Click a topic name (e.g., `order-events`), then go to the **Topic Data** tab. You'll see messages with:

- **Key** — The order ID (e.g., `ORD-ABCD1234`)
- **Value** — The JSON payload deserialized and rendered in the UI
- **Partition / Offset** — Partition assignment and position
- **Timestamp** — When the message was produced

### 3. Check Consumer Groups

Click **Consumers** in the sidebar. You'll see:

| Group ID | Topic | Status |
|----------|-------|--------|
| `shipment-service-group` | `order-events` | Active (concurrency=3) |
| `notification-service-group` | `order-events`, `shipment-events` | Active (concurrency=2 per topic) |

The **Lag** column shows how many messages are pending for each consumer.

### 4. Produce a Test Message

From a topic's detail page, click the **Produce** tab. Enter a key and JSON value, then click **Publish**. The message will be sent to Kafka immediately.

## Troubleshooting

**AKHQ won't start / can't connect to Kafka:**
```bash
docker compose logs akhq
```

**Common issues:**
- Kafka isn't ready yet — AKHQ will retry, but give it a few seconds
- Port 8085 is already in use — change the host port in `docker-compose.yml`
- "Connection refused" — verify Kafka is healthy: `docker compose ps kafka`

## Reference

- AKHQ Docs: https://akhq.io
- GitHub: https://github.com/tchiotludo/akhq
- Version: 0.26.0 (lightweight stable release)
