class ApiEndpoints {
  static const String baseUrl = 'http://localhost:8086';
  static const String users = '/api/v1/users';
  static String user(int id) => '/api/v1/users/$id';
  static const String orders = '/api/v1/orders';
  static String ordersByUser(int userId) => '/api/v1/orders?userId=$userId';
  static const String shipments = '/api/v1/shipments';
  static String shipmentApprove(String id) => '/api/v1/shipments/$id/approve';
  static String shipmentDecline(String id) => '/api/v1/shipments/$id/decline';
  static const String deliveries = '/api/v1/deliveries';
  static String deliveryApprove(String id) => '/api/v1/deliveries/$id/approve';
  static String deliveryDelivered(String id) =>
      '/api/v1/deliveries/$id/delivered';
  static String deliveryNotDelivered(String id) =>
      '/api/v1/deliveries/$id/not-delivered';
}
