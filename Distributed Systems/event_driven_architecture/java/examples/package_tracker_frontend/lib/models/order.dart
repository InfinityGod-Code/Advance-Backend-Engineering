import 'package:flutter/material.dart';
import 'address.dart';

enum OrderStatus {
  created,
  placed,
  confirmed,
  shipped,
  inTransit,
  outForDelivery,
  delivered,
  cancelled;

  String get label {
    switch (this) {
      case OrderStatus.created:
        return 'Created';
      case OrderStatus.placed:
        return 'Placed';
      case OrderStatus.confirmed:
        return 'Confirmed';
      case OrderStatus.shipped:
        return 'Shipped';
      case OrderStatus.inTransit:
        return 'In Transit';
      case OrderStatus.outForDelivery:
        return 'Out for Delivery';
      case OrderStatus.delivered:
        return 'Delivered';
      case OrderStatus.cancelled:
        return 'Cancelled';
    }
  }

  Color get color {
    switch (this) {
      case OrderStatus.created:
        return Colors.blueGrey;
      case OrderStatus.placed:
        return Colors.blue;
      case OrderStatus.confirmed:
        return Colors.indigo;
      case OrderStatus.shipped:
        return Colors.amber.shade700;
      case OrderStatus.inTransit:
        return Colors.orange;
      case OrderStatus.outForDelivery:
        return Colors.deepOrange;
      case OrderStatus.delivered:
        return Colors.green;
      case OrderStatus.cancelled:
        return Colors.red;
    }
  }

  IconData get icon {
    switch (this) {
      case OrderStatus.created:
        return Icons.add_circle_outline;
      case OrderStatus.placed:
        return Icons.receipt_long;
      case OrderStatus.confirmed:
        return Icons.check_circle_outline;
      case OrderStatus.shipped:
        return Icons.local_shipping;
      case OrderStatus.inTransit:
        return Icons.flight;
      case OrderStatus.outForDelivery:
        return Icons.delivery_dining;
      case OrderStatus.delivered:
        return Icons.check_circle;
      case OrderStatus.cancelled:
        return Icons.cancel;
    }
  }
}

class Order {
  final String id;
  final String userId;
  final List<String> items;
  final double totalAmount;
  final Address shippingAddress;
  OrderStatus status;
  final DateTime createdAt;

  Order({
    required this.id,
    required this.userId,
    required this.items,
    required this.totalAmount,
    required this.shippingAddress,
    required this.status,
    required this.createdAt,
  });
}
