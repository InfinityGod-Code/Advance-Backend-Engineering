import 'address.dart';
import 'order_status.dart';
export 'order_status.dart';

class Order {
  final int id;
  final String orderId;
  final int userId;
  final List<String> items;
  final double totalAmount;
  final Address shippingAddress;
  OrderStatus status;
  final DateTime createdAt;
  final DateTime updatedAt;

  Order({
    required this.id,
    required this.orderId,
    required this.userId,
    required this.items,
    required this.totalAmount,
    required this.shippingAddress,
    required this.status,
    required this.createdAt,
    DateTime? updatedAt,
  }) : updatedAt = updatedAt ?? createdAt;

  factory Order.fromJson(Map<String, dynamic> json) => Order(
    id: (json['id'] as num).toInt(),
    orderId: json['orderId'] as String? ?? 'ORD-${json['id']}',
    userId: json['userId'] ?? 0,
    items:
        (json['items'] as List<dynamic>?)?.map((e) => e as String).toList() ??
        [],
    totalAmount: (json['totalAmount'] as num).toDouble(),
    shippingAddress: json['shippingAddress'] != null
        ? Address.fromJson(json['shippingAddress'] as Map<String, dynamic>)
        : Address(street: '', city: '', state: '', zip: ''),
    status: OrderStatus.fromValue(json['status'] as String?),
    createdAt: json['createdAt'] != null
        ? DateTime.parse(json['createdAt'] as String)
        : DateTime.now(),
    updatedAt: json['updatedAt'] != null
        ? DateTime.parse(json['updatedAt'] as String)
        : null,
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'orderId': orderId,
    'userId': userId,
    'items': items,
    'totalAmount': totalAmount,
    'shippingAddress': shippingAddress.toJson(),
    'status': status.value,
    'createdAt': createdAt.toIso8601String(),
    'updatedAt': updatedAt.toIso8601String(),
  };
}
