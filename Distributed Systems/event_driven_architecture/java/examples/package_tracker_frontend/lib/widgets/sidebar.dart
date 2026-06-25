import 'package:flutter/material.dart';

class Sidebar extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onDestinationSelected;

  static const _destinations = (
    labels: ['Customer', 'Seller', 'Delivery'],
    icons: [Icons.person, Icons.store, Icons.local_shipping],
  );

  const Sidebar({
    super.key,
    required this.selectedIndex,
    required this.onDestinationSelected,
  });

  @override
  Widget build(BuildContext context) {
    return NavigationRail(
      selectedIndex: selectedIndex,
      onDestinationSelected: onDestinationSelected,
      labelType: NavigationRailLabelType.all,
      leading: Padding(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Icon(
          Icons.inventory_2,
          size: 32,
          color: Theme.of(context).colorScheme.primary,
        ),
      ),
      destinations: [
        for (var i = 0; i < _destinations.labels.length; i++)
          NavigationRailDestination(
            icon: Icon(_destinations.icons[i]),
            label: Text(_destinations.labels[i]),
          ),
      ],
    );
  }
}
