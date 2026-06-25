import 'package:dio/dio.dart';
import '../models/user.dart';
import 'api_client.dart';
import 'api_endpoints.dart';

class UserService {
  final Dio _dio = ApiClient().dio;

  Future<List<User>> getUsers() async {
    final response = await _dio.get(ApiEndpoints.users);
    return (response.data as List)
        .map((json) => User.fromJson(json as Map<String, dynamic>))
        .toList();
  }

  Future<User> getUserById(int id) async {
    final response = await _dio.get(ApiEndpoints.user(id));
    return User.fromJson(response.data as Map<String, dynamic>);
  }

  Future<User> createUser(Map<String, dynamic> body) async {
    final response = await _dio.post(ApiEndpoints.users, data: body);
    return User.fromJson(response.data as Map<String, dynamic>);
  }
}
