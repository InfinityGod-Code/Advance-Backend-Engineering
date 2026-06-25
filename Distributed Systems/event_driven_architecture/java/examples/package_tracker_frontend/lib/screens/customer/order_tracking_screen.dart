import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../models/order.dart';
import '../../models/tracking_event.dart';
import '../../cubits/order_cubit.dart';
import '../../services/sse_service.dart';
import '../../utils/date_formatter.dart';
import 'widgets/tracking_timeline.dart';
import 'widgets/status_badge.dart';

class OrderTrackingScreen extends StatefulWidget {
  final Order order;

  const OrderTrackingScreen({super.key, required this.order});

  @override
  State<OrderTrackingScreen> createState() => _OrderTrackingScreenState();
}

class _OrderTrackingScreenState extends State<OrderTrackingScreen> {
  late Order _order;
  late List<TrackingEvent> _events;
  SseService? _sseService;
  StreamSubscription<SseEvent>? _subscription;

  @override
  void initState() {
    super.initState();
    _order = widget.order;
    _events = context.read<OrderCubit>().getTracking(_order);
    _connectSse();
  }

  void _connectSse() {
    _sseService = SseService();
    _sseService!.connect();
    _subscription = _sseService!.stream.listen(_onSseEvent, onError: (_) {});
  }

  void _onSseEvent(SseEvent event) {
    if (event.data['orderId'] != _order.orderId) return;

    final current = _order.status;
    switch (event.event) {
      case 'ShipmentStarted':
        if (current.index < OrderStatus.shipped.index) {
          _order.status = OrderStatus.shipped;
        }
        break;
      case 'DeliveryStarted':
        if (current.index < OrderStatus.delivered.index) {
          _order.status = OrderStatus.delivered;
        }
        break;
      default:
        return;
    }

    if (!mounted) return;
    setState(() {
      _events = context.read<OrderCubit>().getTracking(_order);
    });
  }

  @override
  void dispose() {
    _subscription?.cancel();
    _sseService?.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text('Order #${_order.orderId.toUpperCase()}'),
        backgroundColor: theme.colorScheme.inversePrimary,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  _order.status.color.withValues(alpha: 0.15),
                  _order.status.color.withValues(alpha: 0.05),
                  theme.colorScheme.surface,
                ],
              ),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: _order.status.color.withValues(alpha: 0.2),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: _order.status.color.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(
                        _order.status.icon,
                        size: 28,
                        color: _order.status.color,
                      ),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _order.status.label,
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: _order.status.color,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            formatDate(_order.createdAt),
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                      ),
                    ),
                    StatusBadge(status: _order.status),
                  ],
                ),
                const SizedBox(height: 16),
                const Divider(),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Text(
                      'Items',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      '\$${_order.totalAmount.toStringAsFixed(2)}',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: theme.colorScheme.primary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                ..._order.items.map(
                  (item) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      children: [
                        Icon(
                          Icons.circle,
                          size: 6,
                          color: theme.colorScheme.primary,
                        ),
                        const SizedBox(width: 10),
                        Text(item, style: theme.textTheme.bodyMedium),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                const Divider(),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(
                      Icons.local_shipping,
                      size: 16,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Shipping Address',
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  _order.shippingAddress.fullAddress,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'Tracking History',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          TrackingTimeline(events: _events),
        ],
      ),
    );
  }
}
