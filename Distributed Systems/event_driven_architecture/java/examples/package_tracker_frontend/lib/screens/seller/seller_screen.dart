import 'package:flutter/material.dart';

class SellerScreen extends StatelessWidget {
  const SellerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.store, size: 80, color: theme.colorScheme.primary),
            const SizedBox(height: 16),
            Text('Seller Dashboard', style: theme.textTheme.headlineMedium),
            const SizedBox(height: 8),
            Text(
              'Manage inventory, process orders, and update shipping details.',
              style: theme.textTheme.bodyLarge?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
