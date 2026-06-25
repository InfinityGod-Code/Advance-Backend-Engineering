import 'order.dart';

class TrackingEvent {
  final String id;
  final String orderId;
  final OrderStatus status;
  final DateTime timestamp;
  final String location;
  final String description;

  TrackingEvent({
    required this.id,
    required this.orderId,
    required this.status,
    required this.timestamp,
    required this.location,
    required this.description,
  });
}
