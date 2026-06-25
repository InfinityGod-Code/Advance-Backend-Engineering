import 'package:flutter/material.dart';

enum ShipmentStatus {
  pendingApproval,
  shipped,
  notShipped;

  String get label {
    switch (this) {
      case ShipmentStatus.pendingApproval:
        return 'Pending Approval';
      case ShipmentStatus.shipped:
        return 'Shipped';
      case ShipmentStatus.notShipped:
        return 'Not Shipped';
    }
  }

  String get value {
    switch (this) {
      case ShipmentStatus.pendingApproval:
        return 'PENDING_APPROVAL';
      case ShipmentStatus.shipped:
        return 'SHIPPED';
      case ShipmentStatus.notShipped:
        return 'NOT_SHIPPED';
    }
  }

  static ShipmentStatus fromValue(String? v) {
    switch (v?.toUpperCase()) {
      case 'PENDING_APPROVAL':
        return ShipmentStatus.pendingApproval;
      case 'SHIPPED':
        return ShipmentStatus.shipped;
      case 'NOT_SHIPPED':
        return ShipmentStatus.notShipped;
      default:
        return ShipmentStatus.pendingApproval;
    }
  }

  Color get color {
    switch (this) {
      case ShipmentStatus.pendingApproval:
        return Colors.orange;
      case ShipmentStatus.shipped:
        return Colors.green;
      case ShipmentStatus.notShipped:
        return Colors.red;
    }
  }

  IconData get icon {
    switch (this) {
      case ShipmentStatus.pendingApproval:
        return Icons.hourglass_empty;
      case ShipmentStatus.shipped:
        return Icons.check_circle;
      case ShipmentStatus.notShipped:
        return Icons.cancel;
    }
  }
}
