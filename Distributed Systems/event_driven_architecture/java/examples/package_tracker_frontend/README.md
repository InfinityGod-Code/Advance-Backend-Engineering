# Package Tracker Frontend

Flutter web app that visualizes the backend event-driven architecture for package tracking.

## Run Instructions

**Prerequisites:** Flutter 3.44.0+ with Chrome browser.

```bash
flutter pub get
flutter run -d chrome
```

> **Important:** The backend Java service must be running on `http://localhost:8086` before launching.

## Architecture

- **State Management:** BLoC pattern (`flutter_bloc`)
- **HTTP Client:** `dio` (connects to `localhost:8086`)
- **Real-time:** SSE for live event updates
- **Target:** Web only (Chrome)

## Backend API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/users` | Fetch users |
| `GET /api/v1/orders?userId={id}` | Fetch orders by user |
| `GET /api/v1/shipments` | Fetch shipments |
| `POST /api/v1/shipments/{id}/approve` | Approve shipment |
| `POST /api/v1/shipments/{id}/decline` | Decline shipment |
| `GET /api/v1/deliveries` | Fetch deliveries |
| `POST /api/v1/deliveries/{id}/approve` | Approve delivery |
| `POST /api/v1/deliveries/{id}/delivered` | Mark delivered |
| `POST /api/v1/deliveries/{id}/not-delivered` | Mark not delivered |
