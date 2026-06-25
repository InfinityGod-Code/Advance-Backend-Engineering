import 'package:flutter/material.dart';

enum OrderStatus {
  pending,
  created,
  confirmed,
  processing,
  shipped,
  delivered,
  cancelled;

  String get label {
    switch (this) {
      case OrderStatus.pending:
        return 'Pending';
      case OrderStatus.created:
        return 'Created';
      case OrderStatus.confirmed:
        return 'Confirmed';
      case OrderStatus.processing:
        return 'Processing';
      case OrderStatus.shipped:
        return 'Shipped';
      case OrderStatus.delivered:
        return 'Delivered';
      case OrderStatus.cancelled:
        return 'Cancelled';
    }
  }

  String get value {
    switch (this) {
      case OrderStatus.pending:
        return 'PENDING';
      case OrderStatus.created:
        return 'CREATED';
      case OrderStatus.confirmed:
        return 'CONFIRMED';
      case OrderStatus.processing:
        return 'PROCESSING';
      case OrderStatus.shipped:
        return 'SHIPPED';
      case OrderStatus.delivered:
        return 'DELIVERED';
      case OrderStatus.cancelled:
        return 'CANCELLED';
    }
  }

  static OrderStatus fromValue(String? v) {
    switch (v?.toUpperCase()) {
      case 'PENDING':
        return OrderStatus.pending;
      case 'CREATED':
        return OrderStatus.created;
      case 'CONFIRMED':
        return OrderStatus.confirmed;
      case 'PROCESSING':
        return OrderStatus.processing;
      case 'SHIPPED':
        return OrderStatus.shipped;
      case 'DELIVERED':
        return OrderStatus.delivered;
      case 'CANCELLED':
        return OrderStatus.cancelled;
      default:
        return OrderStatus.created;
    }
  }

  Color get color {
    switch (this) {
      case OrderStatus.pending:
        return Colors.blueGrey;
      case OrderStatus.created:
        return Colors.blueGrey;
      case OrderStatus.confirmed:
        return Colors.indigo;
      case OrderStatus.processing:
        return Colors.orange;
      case OrderStatus.shipped:
        return Colors.amber.shade700;
      case OrderStatus.delivered:
        return Colors.green;
      case OrderStatus.cancelled:
        return Colors.red;
    }
  }

  IconData get icon {
    switch (this) {
      case OrderStatus.pending:
        return Icons.hourglass_empty;
      case OrderStatus.created:
        return Icons.add_circle_outline;
      case OrderStatus.confirmed:
        return Icons.check_circle_outline;
      case OrderStatus.processing:
        return Icons.autorenew;
      case OrderStatus.shipped:
        return Icons.local_shipping;
      case OrderStatus.delivered:
        return Icons.check_circle;
      case OrderStatus.cancelled:
        return Icons.cancel;
    }
  }
}
