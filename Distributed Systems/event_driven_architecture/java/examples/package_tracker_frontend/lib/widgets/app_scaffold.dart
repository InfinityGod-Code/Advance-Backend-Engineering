import 'package:flutter/material.dart';
import '../screens/customer/customer_screen.dart';
import '../screens/seller/seller_screen.dart';
import '../screens/delivery/delivery_screen.dart';
import 'sidebar.dart';
import 'bottom_nav_bar.dart';

class AppScaffold extends StatefulWidget {
  const AppScaffold({super.key});

  @override
  State<AppScaffold> createState() => _AppScaffoldState();
}

class _AppScaffoldState extends State<AppScaffold> {
  int _selectedIndex = 0;

  static const _screens = [CustomerScreen(), SellerScreen(), DeliveryScreen()];

  static const _titles = ['Customer', 'Seller', 'Delivery'];

  void _onDestinationSelected(int index) {
    setState(() => _selectedIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth >= 720;

        return Scaffold(
          appBar: AppBar(
            title: Text(_titles[_selectedIndex]),
            backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          ),
          body: isWide
              ? Row(
                  children: [
                    Sidebar(
                      selectedIndex: _selectedIndex,
                      onDestinationSelected: _onDestinationSelected,
                    ),
                    const VerticalDivider(width: 1),
                    Expanded(child: _screens[_selectedIndex]),
                  ],
                )
              : _screens[_selectedIndex],
          bottomNavigationBar: isWide
              ? null
              : BottomNavBar(
                  selectedIndex: _selectedIndex,
                  onDestinationSelected: _onDestinationSelected,
                ),
        );
      },
    );
  }
}
