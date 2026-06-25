import 'package:dio/dio.dart';
import '../models/order.dart';
import 'api_client.dart';
import 'api_endpoints.dart';

class OrderService {
  final Dio _dio = ApiClient().dio;

  Future<List<Order>> getOrdersByUserId(int userId) async {
    final response = await _dio.get(ApiEndpoints.ordersByUser(userId));
    return (response.data as List)
        .map((json) => Order.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  Future<Order> createOrder(Map<String, dynamic> body) async {
    final response = await _dio.post(ApiEndpoints.orders, data: body);
    return Order.fromJson(response.data as Map<String, dynamic>);
  }
}
