import 'package:flutter/material.dart';
import '../models/address.dart';
import '../models/user.dart';
import '../models/order.dart';
import '../models/tracking_event.dart';

class MockDataStore extends ChangeNotifier {
  MockDataStore._() {
    _initMockData();
  }

  static final MockDataStore _instance = MockDataStore._();
  factory MockDataStore() => _instance;

  final List<User> _users = [];
  final List<Order> _orders = [];
  final List<TrackingEvent> _trackingEvents = [];

  List<User> get users => List.unmodifiable(_users);
  List<Order> get orders => List.unmodifiable(_orders);

  List<Order> getOrdersByUser(String userId) =>
      _orders.where((o) => o.userId == userId).toList()
        ..sort((a, b) => b.createdAt.compareTo(a.createdAt));

  List<TrackingEvent> getTrackingByOrder(String orderId) {
    final events = _trackingEvents.where((e) => e.orderId == orderId).toList();
    events.sort((a, b) => a.timestamp.compareTo(b.timestamp));
    return events;
  }

  User? getUserById(String id) {
    try {
      return _users.firstWhere((u) => u.id == id);
    } catch (_) {
      return null;
    }
  }

  int getOrderCount(String userId) =>
      _orders.where((o) => o.userId == userId).length;

  int getActiveOrderCount(String userId) => _orders
      .where(
        (o) =>
            o.userId == userId &&
            o.status != OrderStatus.delivered &&
            o.status != OrderStatus.cancelled,
      )
      .length;

  int getDeliveredOrderCount(String userId) => _orders
      .where((o) => o.userId == userId && o.status == OrderStatus.delivered)
      .length;

  void addUser(User user) {
    _users.add(user);
    notifyListeners();
  }

  void addOrder(Order order) {
    _orders.add(order);
    final now = DateTime.now();
    _trackingEvents.add(
      TrackingEvent(
        id: 'te_${order.id}_${now.millisecondsSinceEpoch}',
        orderId: order.id,
        status: order.status,
        timestamp: now,
        location: 'Online',
        description: 'Order has been placed successfully',
      ),
    );
    notifyListeners();
  }

  void _initMockData() {
    final addr1 = Address(
      street: '45 Park Avenue',
      city: 'Pune',
      state: 'Maharashtra',
      zipCode: '411001',
      country: 'India',
    );
    final addr2 = Address(
      street: '12 Tech Park Road',
      city: 'Bangalore',
      state: 'Karnataka',
      zipCode: '560001',
      country: 'India',
    );
    final addr3 = Address(
      street: '78 Lake View',
      city: 'Mumbai',
      state: 'Maharashtra',
      zipCode: '400001',
      country: 'India',
    );
    final addr4 = Address(
      street: '34 Rose Garden',
      city: 'Chennai',
      state: 'Tamil Nadu',
      zipCode: '600001',
      country: 'India',
    );
    final addr5 = Address(
      street: '56 Hill Top Colony',
      city: 'Hyderabad',
      state: 'Telangana',
      zipCode: '500001',
      country: 'India',
    );

    final users = [
      User(
        id: 'u1',
        name: 'Priya Sharma',
        email: 'priya.sharma@example.com',
        phone: '+91-9123456789',
        address: addr1,
        avatarColor: Colors.teal,
        createdAt: DateTime(2025, 1, 15),
      ),
      User(
        id: 'u2',
        name: 'Rahul Verma',
        email: 'rahul.verma@example.com',
        phone: '+91-9876543210',
        address: addr2,
        avatarColor: Colors.deepPurple,
        createdAt: DateTime(2025, 2, 20),
      ),
      User(
        id: 'u3',
        name: 'Ananya Patel',
        email: 'ananya.patel@example.com',
        phone: '+91-9988776655',
        address: addr3,
        avatarColor: Colors.orange,
        createdAt: DateTime(2025, 3, 10),
      ),
      User(
        id: 'u4',
        name: 'Vikram Singh',
        email: 'vikram.singh@example.com',
        phone: '+91-8877665544',
        address: addr4,
        avatarColor: Colors.pink,
        createdAt: DateTime(2025, 4, 5),
      ),
      User(
        id: 'u5',
        name: 'Neha Gupta',
        email: 'neha.gupta@example.com',
        phone: '+91-7766554433',
        address: addr5,
        avatarColor: Colors.cyan,
        createdAt: DateTime(2025, 5, 1),
      ),
    ];
    _users.addAll(users);

    final ship1 = Address(
      street: '221B Baker Street',
      city: 'London',
      state: 'Greater London',
      zipCode: 'NW16XE',
      country: 'UK',
    );
    final ship2 = Address(
      street: '45 Park Avenue',
      city: 'Pune',
      state: 'Maharashtra',
      zipCode: '411001',
      country: 'India',
    );
    final ship3 = Address(
      street: '12 Tech Park Road',
      city: 'Bangalore',
      state: 'Karnataka',
      zipCode: '560001',
      country: 'India',
    );
    final ship4 = Address(
      street: '78 Lake View',
      city: 'Mumbai',
      state: 'Maharashtra',
      zipCode: '400001',
      country: 'India',
    );
    final ship5 = Address(
      street: '34 Rose Garden',
      city: 'Chennai',
      state: 'Tamil Nadu',
      zipCode: '600001',
      country: 'India',
    );
    final ship6 = Address(
      street: '56 Hill Top Colony',
      city: 'Hyderabad',
      state: 'Telangana',
      zipCode: '500001',
      country: 'India',
    );
    final ship7 = Address(
      street: '10 Downing Street',
      city: 'London',
      state: 'Greater London',
      zipCode: 'SW1A2AA',
      country: 'UK',
    );
    final ship8 = Address(
      street: '1 MG Road',
      city: 'Bangalore',
      state: 'Karnataka',
      zipCode: '560001',
      country: 'India',
    );

    final orders = [
      Order(
        id: 'ORD-2026-1001',
        userId: 'u1',
        items: ['Wireless Headphones', 'USB-C Hub'],
        totalAmount: 2499.99,
        shippingAddress: ship1,
        status: OrderStatus.delivered,
        createdAt: DateTime(2025, 5, 10),
      ),
      Order(
        id: 'ORD-2026-1002',
        userId: 'u1',
        items: ['Mechanical Keyboard', 'Mouse Pad', 'Wrist Rest'],
        totalAmount: 5499.50,
        shippingAddress: ship2,
        status: OrderStatus.inTransit,
        createdAt: DateTime(2025, 6, 1),
      ),
      Order(
        id: 'ORD-2026-1003',
        userId: 'u2',
        items: ['4K Monitor 27"'],
        totalAmount: 31999.00,
        shippingAddress: ship3,
        status: OrderStatus.shipped,
        createdAt: DateTime(2025, 6, 5),
      ),
      Order(
        id: 'ORD-2026-1004',
        userId: 'u2',
        items: ['Webcam', 'Microphone', 'Lighting Kit'],
        totalAmount: 12999.00,
        shippingAddress: ship4,
        status: OrderStatus.created,
        createdAt: DateTime(2025, 6, 10),
      ),
      Order(
        id: 'ORD-2026-1005',
        userId: 'u3',
        items: ['Ergonomic Office Chair'],
        totalAmount: 15999.00,
        shippingAddress: ship5,
        status: OrderStatus.outForDelivery,
        createdAt: DateTime(2025, 6, 8),
      ),
      Order(
        id: 'ORD-2026-1006',
        userId: 'u3',
        items: ['Standing Desk Converter'],
        totalAmount: 22499.00,
        shippingAddress: ship6,
        status: OrderStatus.confirmed,
        createdAt: DateTime(2025, 6, 12),
      ),
      Order(
        id: 'ORD-2026-1007',
        userId: 'u4',
        items: ['Laptop Sleeve 15"', 'USB-C Drive 256GB'],
        totalAmount: 3499.00,
        shippingAddress: ship7,
        status: OrderStatus.delivered,
        createdAt: DateTime(2025, 4, 20),
      ),
      Order(
        id: 'ORD-2026-1008',
        userId: 'u5',
        items: ['Tablet Stand', 'Screen Protector'],
        totalAmount: 1999.00,
        shippingAddress: ship8,
        status: OrderStatus.cancelled,
        createdAt: DateTime(2025, 5, 25),
      ),
    ];
    _orders.addAll(orders);

    _trackingEvents.addAll([
      TrackingEvent(
        id: 'e1',
        orderId: 'ORD-2026-1001',
        status: OrderStatus.placed,
        timestamp: DateTime(2025, 5, 10, 9, 30),
        location: 'Online',
        description: 'Order placed successfully',
      ),
      TrackingEvent(
        id: 'e2',
        orderId: 'ORD-2026-1001',
        status: OrderStatus.confirmed,
        timestamp: DateTime(2025, 5, 10, 10, 15),
        location: 'Warehouse A, Chicago',
        description: 'Payment confirmed, order processing',
      ),
      TrackingEvent(
        id: 'e3',
        orderId: 'ORD-2026-1001',
        status: OrderStatus.shipped,
        timestamp: DateTime(2025, 5, 11, 8, 0),
        location: 'Distribution Center, Chicago',
        description: 'Package shipped via FastExpress',
      ),
      TrackingEvent(
        id: 'e4',
        orderId: 'ORD-2026-1001',
        status: OrderStatus.inTransit,
        timestamp: DateTime(2025, 5, 12, 14, 30),
        location: 'Transit Hub, Denver',
        description: 'Package arrived at hub, en route',
      ),
      TrackingEvent(
        id: 'e5',
        orderId: 'ORD-2026-1001',
        status: OrderStatus.outForDelivery,
        timestamp: DateTime(2025, 5, 13, 7, 45),
        location: 'Local Facility, SF',
        description: 'Package out for delivery',
      ),
      TrackingEvent(
        id: 'e6',
        orderId: 'ORD-2026-1001',
        status: OrderStatus.delivered,
        timestamp: DateTime(2025, 5, 13, 15, 20),
        location: '123 Main St, San Francisco',
        description: 'Delivered, signed by Alice',
      ),

      TrackingEvent(
        id: 'e7',
        orderId: 'ORD-2026-1002',
        status: OrderStatus.placed,
        timestamp: DateTime(2025, 6, 1, 11, 0),
        location: 'Online',
        description: 'Order placed',
      ),
      TrackingEvent(
        id: 'e8',
        orderId: 'ORD-2026-1002',
        status: OrderStatus.confirmed,
        timestamp: DateTime(2025, 6, 1, 11, 45),
        location: 'Warehouse B, Dallas',
        description: 'Confirmed',
      ),
      TrackingEvent(
        id: 'e9',
        orderId: 'ORD-2026-1002',
        status: OrderStatus.shipped,
        timestamp: DateTime(2025, 6, 2, 9, 0),
        location: 'DC, Dallas',
        description: 'Shipped via SwiftShip',
      ),
      TrackingEvent(
        id: 'e10',
        orderId: 'ORD-2026-1002',
        status: OrderStatus.inTransit,
        timestamp: DateTime(2025, 6, 3, 16, 0),
        location: 'Transit Hub, Phoenix',
        description: 'In transit to destination',
      ),

      TrackingEvent(
        id: 'e11',
        orderId: 'ORD-2026-1003',
        status: OrderStatus.placed,
        timestamp: DateTime(2025, 6, 5, 14, 0),
        location: 'Online',
        description: 'Order placed',
      ),
      TrackingEvent(
        id: 'e12',
        orderId: 'ORD-2026-1003',
        status: OrderStatus.confirmed,
        timestamp: DateTime(2025, 6, 5, 14, 30),
        location: 'Warehouse C, Seattle',
        description: 'Confirmed',
      ),
      TrackingEvent(
        id: 'e13',
        orderId: 'ORD-2026-1003',
        status: OrderStatus.shipped,
        timestamp: DateTime(2025, 6, 6, 10, 0),
        location: 'DC, Seattle',
        description: 'Shipped via QuickPost',
      ),

      TrackingEvent(
        id: 'e14',
        orderId: 'ORD-2026-1005',
        status: OrderStatus.placed,
        timestamp: DateTime(2025, 6, 8, 8, 0),
        location: 'Online',
        description: 'Order placed',
      ),
      TrackingEvent(
        id: 'e15',
        orderId: 'ORD-2026-1005',
        status: OrderStatus.confirmed,
        timestamp: DateTime(2025, 6, 8, 8, 30),
        location: 'Warehouse A, NY',
        description: 'Confirmed',
      ),
      TrackingEvent(
        id: 'e16',
        orderId: 'ORD-2026-1005',
        status: OrderStatus.shipped,
        timestamp: DateTime(2025, 6, 9, 7, 0),
        location: 'DC, New York',
        description: 'Shipped',
      ),
      TrackingEvent(
        id: 'e17',
        orderId: 'ORD-2026-1005',
        status: OrderStatus.inTransit,
        timestamp: DateTime(2025, 6, 10, 12, 0),
        location: 'Transit Hub, Boston',
        description: 'In transit',
      ),
      TrackingEvent(
        id: 'e18',
        orderId: 'ORD-2026-1005',
        status: OrderStatus.outForDelivery,
        timestamp: DateTime(2025, 6, 11, 8, 15),
        location: 'Local Facility, Boston',
        description: 'Out for delivery',
      ),

      TrackingEvent(
        id: 'e19',
        orderId: 'ORD-2026-1007',
        status: OrderStatus.placed,
        timestamp: DateTime(2025, 4, 20, 10, 0),
        location: 'Online',
        description: 'Order placed',
      ),
      TrackingEvent(
        id: 'e20',
        orderId: 'ORD-2026-1007',
        status: OrderStatus.delivered,
        timestamp: DateTime(2025, 4, 21, 16, 0),
        location: '456 Oak Ave',
        description: 'Delivered',
      ),
    ]);
  }
}
