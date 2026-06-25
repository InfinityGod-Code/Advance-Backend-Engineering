import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../models/order.dart';
import '../models/tracking_event.dart';
import '../services/order_service.dart';

abstract class OrderState extends Equatable {
  const OrderState();
}

class OrderInitial extends OrderState {
  const OrderInitial();
  @override
  List<Object?> get props => [];
}

class OrderLoading extends OrderState {
  const OrderLoading();
  @override
  List<Object?> get props => [];
}

class OrderLoaded extends OrderState {
  final List<Order> orders;
  final Map<String, List<TrackingEvent>> tracking;
  const OrderLoaded(this.orders, this.tracking);
  @override
  List<Object?> get props => [orders, tracking];
}

class OrderError extends OrderState {
  final String message;
  const OrderError(this.message);
  @override
  List<Object?> get props => [message];
}

class OrderCubit extends Cubit<OrderState> {
  final OrderService _service = OrderService();

  OrderCubit() : super(const OrderInitial());

  Future<void> loadByUserId(int userId) async {
    emit(const OrderLoading());
    try {
      final orders = await _service.getOrdersByUserId(userId);
      final tracking = <String, List<TrackingEvent>>{};
      for (final order in orders) {
        tracking[order.orderId] = _generateTracking(order);
      }
      emit(OrderLoaded(orders, tracking));
    } catch (e) {
      emit(OrderError('Failed to load orders: $e'));
    }
  }

  Future<void> createOrder(Map<String, dynamic> body, int userId) async {
    try {
      await _service.createOrder(body);
      await loadByUserId(userId);
    } catch (e) {
      emit(OrderError('Failed to create order: $e'));
    }
  }

  List<TrackingEvent> getTracking(Order order) {
    return _generateTracking(order);
  }

  List<TrackingEvent> _generateTracking(Order order) {
    final progression = OrderStatus.values;
    final currentIndex = progression.indexOf(order.status);
    if (currentIndex < 0) return [];

    final now = DateTime.now();
    final totalSec = now.difference(order.createdAt).inSeconds;
    final segment = totalSec ~/ (currentIndex + 1);

    const locations = [
      'Online',
      'Warehouse',
      'Processing Center',
      'Distribution Center',
      'Local Hub',
      'Customer Location',
    ];
    const descriptions = [
      'Order placed successfully',
      'Payment confirmed, order is being prepared',
      'Order is being processed',
      'Package has been shipped',
      'Package is out for delivery',
      'Package has been delivered',
    ];

    final events = <TrackingEvent>[];
    for (int i = 0; i <= currentIndex; i++) {
      events.add(
        TrackingEvent(
          id: 'te_${order.id}_$i',
          orderId: order.orderId,
          status: progression[i],
          timestamp: order.createdAt.add(Duration(seconds: segment * i)),
          location: locations[i < locations.length ? i : locations.length - 1],
          description:
              descriptions[i < descriptions.length
                  ? i
                  : descriptions.length - 1],
        ),
      );
    }
    return events;
  }
}
