import 'package:dio/dio.dart';
import '../models/shipment.dart';
import 'api_client.dart';
import 'api_endpoints.dart';

class ShipmentService {
  final Dio _dio = ApiClient().dio;

  Future<List<Shipment>> getShipments({String? status}) async {
    final query = status != null ? {'status': status} : null;
    final response = await _dio.get(
      ApiEndpoints.shipments,
      queryParameters: query,
    );
    return (response.data as List)
        .map((json) => Shipment.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  Future<void> approveShipment(String shipmentId) async {
    await _dio.post(ApiEndpoints.shipmentApprove(shipmentId));
  }

  Future<void> declineShipment(String shipmentId) async {
    await _dio.post(ApiEndpoints.shipmentDecline(shipmentId));
  }
}
