import 'package:dio/dio.dart';
import '../models/delivery.dart';
import 'api_client.dart';
import 'api_endpoints.dart';

class DeliveryService {
  final Dio _dio = ApiClient().dio;

  Future<List<Delivery>> getDeliveries({String? status}) async {
    final query = status != null ? {'status': status} : null;
    final response = await _dio.get(
      ApiEndpoints.deliveries,
      queryParameters: query,
    );
    return (response.data as List)
        .map((json) => Delivery.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  Future<void> approveDelivery(String deliveryId) async {
    await _dio.post(ApiEndpoints.deliveryApprove(deliveryId));
  }

  Future<void> markDelivered(String deliveryId) async {
    await _dio.post(ApiEndpoints.deliveryDelivered(deliveryId));
  }

  Future<void> markNotDelivered(String deliveryId) async {
    await _dio.post(ApiEndpoints.deliveryNotDelivered(deliveryId));
  }
}
