import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../models/user.dart';
import '../../models/order.dart';
import '../../cubits/order_cubit.dart';
import '../../widgets/stat_tile.dart';
import 'widgets/order_card.dart';
import 'create_order_sheet.dart';
import 'order_tracking_screen.dart';

class UserOrdersScreen extends StatefulWidget {
  final User user;

  const UserOrdersScreen({super.key, required this.user});

  @override
  State<UserOrdersScreen> createState() => _UserOrdersScreenState();
}

class _UserOrdersScreenState extends State<UserOrdersScreen> {
  @override
  void initState() {
    super.initState();
    context.read<OrderCubit>().loadByUserId(widget.user.id);
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<OrderCubit, OrderState>(
      builder: (context, state) {
        if (state is OrderLoading) {
          return Scaffold(
            appBar: AppBar(title: Text(widget.user.name)),
            body: const Center(child: CircularProgressIndicator()),
          );
        }
        if (state is OrderError) {
          return Scaffold(
            appBar: AppBar(title: Text(widget.user.name)),
            body: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.error_outline, size: 48, color: Colors.red),
                  const SizedBox(height: 8),
                  Text(state.message, textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  FilledButton(
                    onPressed: () =>
                        context.read<OrderCubit>().loadByUserId(widget.user.id),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
          );
        }
        if (state is OrderLoaded) {
          return _UserOrdersBody(state: state, user: widget.user);
        }
        return Scaffold(
          appBar: AppBar(title: Text(widget.user.name)),
          body: const SizedBox.shrink(),
        );
      },
    );
  }
}

class _UserOrdersBody extends StatelessWidget {
  final OrderLoaded state;
  final User user;

  const _UserOrdersBody({required this.state, required this.user});

  int get _total => state.orders.length;
  int get _active => state.orders
      .where(
        (o) => o.status.name != 'delivered' && o.status.name != 'cancelled',
      )
      .length;
  int get _delivered =>
      state.orders.where((o) => o.status.name == 'delivered').length;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

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
                      Colors.indigo.withValues(alpha: 0.9),
                      Colors.indigo.withValues(alpha: 0.6),
                      Colors.indigo.withValues(alpha: 0.4),
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
                                crossAxisAlignment: CrossAxisAlignment.start,
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
                  StatTile(
                    icon: Icons.receipt_long,
                    value: '$_total',
                    label: 'Total',
                    color: Colors.indigo,
                  ),
                  const SizedBox(width: 8),
                  StatTile(
                    icon: Icons.pending,
                    value: '$_active',
                    label: 'Active',
                    color: Colors.orange,
                  ),
                  const SizedBox(width: 8),
                  StatTile(
                    icon: Icons.check_circle,
                    value: '$_delivered',
                    label: 'Delivered',
                    color: Colors.green,
                  ),
                ],
              ),
            ),
          ),
          if (state.orders.isEmpty)
            SliverFillRemaining(
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.shopping_bag_outlined,
                      size: 64,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'No orders yet',
                      style: theme.textTheme.bodyLarge?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
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
              delegate: SliverChildBuilderDelegate(
                (context, index) => OrderCard(
                  order: state.orders[index],
                  onTap: () => _openTracking(context, state.orders[index]),
                ),
                childCount: state.orders.length,
              ),
            ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _createOrder(context),
        tooltip: 'New Order',
        child: const Icon(Icons.add),
      ),
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
