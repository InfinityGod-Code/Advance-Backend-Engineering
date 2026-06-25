import 'package:flutter/material.dart';
import '../../../models/order.dart';

class StatusBadge extends StatelessWidget {
  final OrderStatus status;
  final bool compact;

  const StatusBadge({super.key, required this.status, this.compact = false});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: compact ? 8 : 12,
        vertical: compact ? 3 : 6,
      ),
      decoration: BoxDecoration(
        color: status.color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: status.color.withValues(alpha: 0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(status.icon, size: compact ? 12 : 16, color: status.color),
          if (compact) const SizedBox(width: 4) else const SizedBox(width: 6),
          Text(
            status.label,
            style: TextStyle(
              fontSize: compact ? 11 : 13,
              fontWeight: FontWeight.w600,
              color: status.color,
              letterSpacing: 0.3,
            ),
          ),
        ],
      ),
    );
  }
}
