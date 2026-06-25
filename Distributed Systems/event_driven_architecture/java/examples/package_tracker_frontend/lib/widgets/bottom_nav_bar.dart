import 'package:flutter/material.dart';

class BottomNavBar extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onDestinationSelected;

  static const _destinations = (
    labels: ['Customer', 'Seller', 'Delivery'],
    icons: [Icons.person, Icons.store, Icons.local_shipping],
  );

  const BottomNavBar({
    super.key,
    required this.selectedIndex,
    required this.onDestinationSelected,
  });

  @override
  Widget build(BuildContext context) {
    return NavigationBar(
      selectedIndex: selectedIndex,
      onDestinationSelected: onDestinationSelected,
      destinations: [
        for (var i = 0; i < _destinations.labels.length; i++)
          NavigationDestination(
            icon: Icon(_destinations.icons[i]),
            label: _destinations.labels[i],
          ),
      ],
    );
  }
}
