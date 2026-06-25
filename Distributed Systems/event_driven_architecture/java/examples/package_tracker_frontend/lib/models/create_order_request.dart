import 'address.dart';

class CreateOrderRequest {
  final String? orderId;
  final int userId;
  final String? status;
  final double totalAmount;
  final Address? shippingAddress;

  CreateOrderRequest({
    this.orderId,
    required this.userId,
    this.status,
    required this.totalAmount,
    this.shippingAddress,
  });

  Map<String, dynamic> toJson() => {
    if (orderId != null) 'orderId': orderId,
    'user': {'id': userId},
    if (status != null) 'status': status,
    'totalAmount': totalAmount,
    if (shippingAddress != null) 'shippingAddress': shippingAddress!.toJson(),
  };
}
