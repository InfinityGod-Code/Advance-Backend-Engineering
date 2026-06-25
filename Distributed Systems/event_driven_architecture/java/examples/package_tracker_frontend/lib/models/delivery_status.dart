import 'package:flutter/material.dart';

enum DeliveryStatus {
  pendingDelivery,
  outForDelivery,
  delivered,
  notDelivered;

  String get label {
    switch (this) {
      case DeliveryStatus.pendingDelivery:
        return 'Pending Delivery';
      case DeliveryStatus.outForDelivery:
        return 'Out for Delivery';
      case DeliveryStatus.delivered:
        return 'Delivered';
      case DeliveryStatus.notDelivered:
        return 'Not Delivered';
    }
  }

  String get value {
    switch (this) {
      case DeliveryStatus.pendingDelivery:
        return 'PENDING_DELIVERY';
      case DeliveryStatus.outForDelivery:
        return 'OUT_FOR_DELIVERY';
      case DeliveryStatus.delivered:
        return 'DELIVERED';
      case DeliveryStatus.notDelivered:
        return 'NOT_DELIVERED';
    }
  }

  static DeliveryStatus fromValue(String? v) {
    switch (v?.toUpperCase()) {
      case 'PENDING_DELIVERY':
        return DeliveryStatus.pendingDelivery;
      case 'OUT_FOR_DELIVERY':
        return DeliveryStatus.outForDelivery;
      case 'DELIVERED':
        return DeliveryStatus.delivered;
      case 'NOT_DELIVERED':
        return DeliveryStatus.notDelivered;
      default:
        return DeliveryStatus.pendingDelivery;
    }
  }

  Color get color {
    switch (this) {
      case DeliveryStatus.pendingDelivery:
        return Colors.orange;
      case DeliveryStatus.outForDelivery:
        return Colors.blue;
      case DeliveryStatus.delivered:
        return Colors.green;
      case DeliveryStatus.notDelivered:
        return Colors.red;
    }
  }

  IconData get icon {
    switch (this) {
      case DeliveryStatus.pendingDelivery:
        return Icons.hourglass_empty;
      case DeliveryStatus.outForDelivery:
        return Icons.delivery_dining;
      case DeliveryStatus.delivered:
        return Icons.check_circle;
      case DeliveryStatus.notDelivered:
        return Icons.cancel;
    }
  }
}
