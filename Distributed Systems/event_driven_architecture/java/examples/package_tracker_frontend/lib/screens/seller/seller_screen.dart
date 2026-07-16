import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../cubits/shipment_cubit.dart';
import '../../models/shipment.dart';
import '../../models/shipment_status.dart';
import 'widgets/shipment_card.dart';

class SellerScreen extends StatefulWidget {
  const SellerScreen({super.key});

  @override
  State<SellerScreen> createState() => _SellerScreenState();
}

class _SellerScreenState extends State<SellerScreen> {


  @override
  void initState() {
    context.read<ShipmentCubit>().loadShipments();
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ShipmentCubit, ShipmentState>(
      builder: (context, state) {
        if (state is ShipmentLoading) {
          return const Center(child: CircularProgressIndicator());
        }
        if (state is ShipmentError) {
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
                      context.read<ShipmentCubit>().loadShipments(),
                  child: const Text('Retry'),
                ),
              ],
            ),
          );
        }
        if (state is ShipmentLoaded) {
          return _SellerBody(shipments: state.shipments);
        }
        return const SizedBox.shrink();
      },
    );
  }
}

class _SellerBody extends StatefulWidget {
  final List<Shipment> shipments;
  const _SellerBody({required this.shipments});

  @override
  State<_SellerBody> createState() => _SellerBodyState();
}

class _SellerBodyState extends State<_SellerBody>
    with SingleTickerProviderStateMixin {
  late final TabController _tabCtrl;

  static const _tabs = ['Pending', 'Shipped', 'Not Shipped', 'All'];

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

  List<Shipment> get _filtered {
    switch (_tabCtrl.index) {
      case 0:
        return widget.shipments
            .where((s) => s.status == ShipmentStatus.pendingApproval)
            .toList();
      case 1:
        return widget.shipments
            .where((s) => s.status == ShipmentStatus.shipped)
            .toList();
      case 2:
        return widget.shipments
            .where((s) => s.status == ShipmentStatus.notShipped)
            .toList();
      default:
        return widget.shipments;
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
                      const Color(0xFF1B3A4B),
                      const Color(0xFF2D5A6E),
                      theme.colorScheme.primary.withValues(alpha: 0.7),
                    ],
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(24, 50, 24, 16),
                    child: Row(
                      children: [
                        const Icon(Icons.store, color: Colors.white, size: 28),
                        const SizedBox(width: 10),
                        Text(
                          'Seller Dashboard',
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
                            '${widget.shipments.length} shipments',
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
                      Icons.inventory_2_outlined,
                      size: 64,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'No shipments in this category',
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
                final shipment = displayed[index];
                return ShipmentCard(
                  shipment: shipment,
                  onApprove: shipment.status == ShipmentStatus.pendingApproval
                      ? () {
                          context.read<ShipmentCubit>().approve(
                            shipment.shipmentId,
                          );
                        }
                      : null,
                  onDecline: shipment.status == ShipmentStatus.pendingApproval
                      ? () {
                          context.read<ShipmentCubit>().decline(
                            shipment.shipmentId,
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
