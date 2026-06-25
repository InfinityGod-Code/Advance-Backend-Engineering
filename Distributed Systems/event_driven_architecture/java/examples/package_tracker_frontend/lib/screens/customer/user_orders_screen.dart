import 'package:flutter/material.dart';
import '../../models/user.dart';
import '../../models/order.dart';
import '../../data/mock_data.dart';
import 'widgets/order_card.dart';
import 'create_order_sheet.dart';
import 'order_tracking_screen.dart';

class UserOrdersScreen extends StatelessWidget {
  final User user;

  const UserOrdersScreen({super.key, required this.user});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: MockDataStore(),
      builder: (context, _) {
        final store = MockDataStore();
        final orders = store.getOrdersByUser(user.id);
        final total = orders.length;
        final active = store.getActiveOrderCount(user.id);
        final delivered = store.getDeliveredOrderCount(user.id);

        return Scaffold(
          body: CustomScrollView(
            slivers: [
              SliverAppBar(
                expandedHeight: 200,
                pinned: true,
                stretch: true,
                flexibleSpace: FlexibleSpaceBar(
                  background: Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          user.avatarColor.withValues(alpha: 0.9),
                          user.avatarColor.withValues(alpha: 0.6),
                          user.avatarColor.withValues(alpha: 0.4),
                        ],
                      ),
                    ),
                    child: SafeArea(
                      child: Padding(
                        padding: const EdgeInsets.fromLTRB(24, 60, 24, 16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                CircleAvatar(
                                  radius: 30,
                                  backgroundColor: Colors.white.withValues(
                                    alpha: 0.25,
                                  ),
                                  child: Text(
                                    user.initials,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 22,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 16),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        user.name,
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 22,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        user.email,
                                        style: TextStyle(
                                          color: Colors.white.withValues(
                                            alpha: 0.8,
                                          ),
                                          fontSize: 13,
                                        ),
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                  child: Row(
                    children: [
                      _StatTile(
                        icon: Icons.receipt_long,
                        value: '$total',
                        label: 'Total',
                        color: Colors.indigo,
                      ),
                      const SizedBox(width: 8),
                      _StatTile(
                        icon: Icons.pending,
                        value: '$active',
                        label: 'Active',
                        color: Colors.orange,
                      ),
                      const SizedBox(width: 8),
                      _StatTile(
                        icon: Icons.check_circle,
                        value: '$delivered',
                        label: 'Delivered',
                        color: Colors.green,
                      ),
                    ],
                  ),
                ),
              ),
              if (orders.isEmpty)
                SliverFillRemaining(
                  child: Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.shopping_bag_outlined,
                          size: 64,
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'No orders yet',
                          style: Theme.of(context).textTheme.bodyLarge
                              ?.copyWith(
                                color: Theme.of(
                                  context,
                                ).colorScheme.onSurfaceVariant,
                              ),
                        ),
                        const SizedBox(height: 8),
                        FilledButton.tonalIcon(
                          onPressed: () => _createOrder(context),
                          icon: const Icon(Icons.add),
                          label: const Text('Create first order'),
                        ),
                      ],
                    ),
                  ),
                )
              else
                SliverList(
                  delegate: SliverChildBuilderDelegate((context, index) {
                    final order = orders[index];
                    return OrderCard(
                      order: order,
                      onTap: () => _openTracking(context, order),
                    );
                  }, childCount: orders.length),
                ),
            ],
          ),
          floatingActionButton: FloatingActionButton(
            onPressed: () => _createOrder(context),
            tooltip: 'New Order',
            child: const Icon(Icons.add),
          ),
        );
      },
    );
  }

  void _createOrder(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (_) => CreateOrderSheet(userId: user.id),
    );
  }

  void _openTracking(BuildContext context, Order order) {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => OrderTrackingScreen(order: order)),
    );
  }
}

class _StatTile extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final Color color;

  const _StatTile({
    required this.icon,
    required this.value,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: color.withValues(alpha: 0.15)),
        ),
        child: Column(
          children: [
            Icon(icon, size: 20, color: color),
            const SizedBox(height: 6),
            Text(
              value,
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              label,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
