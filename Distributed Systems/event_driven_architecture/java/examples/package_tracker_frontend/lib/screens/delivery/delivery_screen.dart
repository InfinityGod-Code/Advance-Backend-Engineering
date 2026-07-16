import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../cubits/delivery_cubit.dart';
import '../../models/delivery.dart';
import '../../models/delivery_status.dart';
import 'widgets/delivery_card.dart';

class DeliveryScreen extends StatefulWidget {
  const DeliveryScreen({super.key});

  @override
  State<DeliveryScreen> createState() => _DeliveryScreenState();
}

class _DeliveryScreenState extends State<DeliveryScreen> {


  @override
  void initState() {
    context.read<DeliveryCubit>().loadDeliveries();
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<DeliveryCubit, DeliveryState>(
      builder: (context, state) {
        if (state is DeliveryLoading) {
          return const Center(child: CircularProgressIndicator());
        }
        if (state is DeliveryError) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline, size: 48, color: Colors.red),
                const SizedBox(height: 8),
                Text(state.message, textAlign: TextAlign.center),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () =>
                      context.read<DeliveryCubit>().loadDeliveries(),
                  child: const Text('Retry'),
                ),
              ],
            ),
          );
        }
        if (state is DeliveryLoaded) {
          return _DeliveryBody(deliveries: state.deliveries);
        }
        return const SizedBox.shrink();
      },
    );
  }
}

class _DeliveryBody extends StatefulWidget {
  final List<Delivery> deliveries;
  const _DeliveryBody({required this.deliveries});

  @override
  State<_DeliveryBody> createState() => _DeliveryBodyState();
}

class _DeliveryBodyState extends State<_DeliveryBody>
    with SingleTickerProviderStateMixin {
  late final TabController _tabCtrl;

  static const _tabs = [
    'Pending',
    'Out for Delivery',
    'Delivered',
    'Not Delivered',
    'All',
  ];

  @override
  void initState() {
    super.initState();
    _tabCtrl = TabController(length: _tabs.length, vsync: this);
    _tabCtrl.addListener((){
      setState(() {

      });
    });
  }

  @override
  void dispose() {
    _tabCtrl.dispose();
    super.dispose();
  }

  List<Delivery> get _filtered {
    switch (_tabCtrl.index) {
      case 0:
        return widget.deliveries
            .where((d) => d.status == DeliveryStatus.pendingDelivery)
            .toList();
      case 1:
        return widget.deliveries
            .where((d) => d.status == DeliveryStatus.outForDelivery)
            .toList();
      case 2:
        return widget.deliveries
            .where((d) => d.status == DeliveryStatus.delivered)
            .toList();
      case 3:
        return widget.deliveries
            .where((d) => d.status == DeliveryStatus.notDelivered)
            .toList();
      default:
        return widget.deliveries;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final displayed = _filtered;
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 140,
            pinned: true,
            stretch: true,
            backgroundColor: Colors.transparent,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      const Color(0xFF2E4A2E),
                      const Color(0xFF3D6B3D),
                      Colors.teal.withValues(alpha: 0.7),
                    ],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(24, 50, 24, 16),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.local_shipping,
                          color: Colors.white,
                          size: 28,
                        ),
                        const SizedBox(width: 10),
                        Text(
                          'Delivery Dashboard',
                          style: theme.textTheme.headlineSmall?.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            '${widget.deliveries.length} deliveries',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.w500,
                              fontSize: 13,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: TabBar(
              controller: _tabCtrl,
              isScrollable: true,
              labelColor: theme.colorScheme.primary,
              unselectedLabelColor: theme.colorScheme.onSurfaceVariant,
              indicatorColor: theme.colorScheme.primary,
              tabs: _tabs.map((t) => Tab(text: t)).toList(),
            ),
          ),
          if (displayed.isEmpty)
            SliverFillRemaining(
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.delivery_dining_outlined,
                      size: 64,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'No deliveries in this category',
                      style: theme.textTheme.bodyLarge?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
            )
          else
            SliverList(
              delegate: SliverChildBuilderDelegate((context, index) {
                final delivery = displayed[index];
                return DeliveryCard(
                  delivery: delivery,
                  onApprove: delivery.status == DeliveryStatus.pendingDelivery
                      ? () {
                          context.read<DeliveryCubit>().approve(
                            delivery.deliveryId,
                          );
                        }
                      : null,
                  onDelivered: delivery.status == DeliveryStatus.outForDelivery
                      ? () {
                          context.read<DeliveryCubit>().delivered(
                            delivery.deliveryId,
                          );
                        }
                      : null,
                  onNotDelivered:
                      delivery.status == DeliveryStatus.outForDelivery
                      ? () {
                          context.read<DeliveryCubit>().notDelivered(
                            delivery.deliveryId,
                          );
                        }
                      : null,
                );
              }, childCount: displayed.length),
            ),
        ],
      ),
    );
  }
}
