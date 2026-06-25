import 'package:flutter/material.dart';
import '../../../models/delivery.dart';
import '../../../models/delivery_status.dart';
import '../../../widgets/app_card.dart';

class DeliveryCard extends StatelessWidget {
  final Delivery delivery;
  final VoidCallback? onApprove;
  final VoidCallback? onDelivered;
  final VoidCallback? onNotDelivered;

  const DeliveryCard({
    super.key,
    required this.delivery,
    this.onApprove,
    this.onDelivered,
    this.onNotDelivered,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: delivery.status.color.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  delivery.status.icon,
                  size: 20,
                  color: delivery.status.color,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      delivery.deliveryId,
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.5,
                      ),
                    ),
                    Text(
                      'Order ${delivery.orderId}',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: delivery.status.color.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: delivery.status.color.withValues(alpha: 0.4),
                  ),
                ),
                child: Text(
                  delivery.status.label,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: delivery.status.color,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(height: 1),
          const SizedBox(height: 10),
          Row(
            children: [
              Icon(
                Icons.person_outline,
                size: 14,
                color: theme.colorScheme.onSurfaceVariant,
              ),
              const SizedBox(width: 4),
              Text(
                'Customer #${delivery.customerId}',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const Spacer(),
              Text(
                'Shipment: ${delivery.shipmentId}',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                  fontSize: 11,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              Icon(
                Icons.currency_rupee,
                size: 14,
                color: theme.colorScheme.primary,
              ),
              const SizedBox(width: 2),
              Text(
                '\$${delivery.totalAmount.toStringAsFixed(2)}',
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: theme.colorScheme.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Row(
            children: [
              Icon(
                Icons.location_on_outlined,
                size: 14,
                color: theme.colorScheme.onSurfaceVariant,
              ),
              const SizedBox(width: 4),
              Expanded(
                child: Text(
                  delivery.shippingAddress,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          if (delivery.status == DeliveryStatus.pendingDelivery &&
              onApprove != null) ...[
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: onApprove,
                icon: const Icon(Icons.delivery_dining, size: 16),
                label: const Text('Mark Out for Delivery'),
                style: FilledButton.styleFrom(
                  backgroundColor: Colors.blue,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
            ),
          ],
          if (delivery.status == DeliveryStatus.outForDelivery &&
              (onDelivered != null || onNotDelivered != null)) ...[
            const SizedBox(height: 12),
            Row(
              children: [
                if (onNotDelivered != null)
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: onNotDelivered,
                      icon: const Icon(Icons.cancel, size: 16),
                      label: const Text('Not Delivered'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.red,
                        side: const BorderSide(color: Colors.red),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                    ),
                  ),
                if (onDelivered != null && onNotDelivered != null)
                  const SizedBox(width: 10),
                if (onDelivered != null)
                  Expanded(
                    child: FilledButton.icon(
                      onPressed: onDelivered,
                      icon: const Icon(Icons.check_circle, size: 16),
                      label: const Text('Delivered'),
                      style: FilledButton.styleFrom(
                        backgroundColor: Colors.green,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
