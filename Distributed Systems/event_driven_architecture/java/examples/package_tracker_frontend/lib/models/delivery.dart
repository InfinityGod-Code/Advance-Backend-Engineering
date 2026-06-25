import 'delivery_status.dart';

class Delivery {
  final int id;
  final String deliveryId;
  final String orderId;
  final String shipmentId;
  final String customerId;
  final double totalAmount;
  final String shippingStreet;
  final String shippingCity;
  final String shippingState;
  final String shippingZip;
  final DeliveryStatus status;
  final DateTime createdAt;
  final DateTime updatedAt;

  Delivery({
    required this.id,
    required this.deliveryId,
    required this.orderId,
    required this.shipmentId,
    required this.customerId,
    required this.totalAmount,
    required this.shippingStreet,
    required this.shippingCity,
    required this.shippingState,
    required this.shippingZip,
    required this.status,
    required this.createdAt,
    DateTime? updatedAt,
  }) : updatedAt = updatedAt ?? createdAt;

  String get shippingAddress =>
      '$shippingStreet, $shippingCity, $shippingState $shippingZip';

  factory Delivery.fromJson(Map<String, dynamic> json) => Delivery(
    id: (json['id'] as num).toInt(),
    deliveryId: json['deliveryId'] as String,
    orderId: json['orderId'] as String,
    shipmentId: json['shipmentId'] as String? ?? '',
    customerId: json['customerId'] as String,
    totalAmount: (json['totalAmount'] as num).toDouble(),
    shippingStreet: json['shippingStreet'] as String? ?? '',
    shippingCity: json['shippingCity'] as String? ?? '',
    shippingState: json['shippingState'] as String? ?? '',
    shippingZip: json['shippingZip'] as String? ?? '',
    status: DeliveryStatus.fromValue(json['status'] as String?),
    createdAt: json['createdAt'] != null
        ? DateTime.parse(json['createdAt'] as String)
        : DateTime.now(),
    updatedAt: json['updatedAt'] != null
        ? DateTime.parse(json['updatedAt'] as String)
        : null,
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'deliveryId': deliveryId,
    'orderId': orderId,
    'shipmentId': shipmentId,
    'customerId': customerId,
    'totalAmount': totalAmount,
    'shippingStreet': shippingStreet,
    'shippingCity': shippingCity,
    'shippingState': shippingState,
    'shippingZip': shippingZip,
    'status': status.value,
    'createdAt': createdAt.toIso8601String(),
    'updatedAt': updatedAt.toIso8601String(),
  };
}
