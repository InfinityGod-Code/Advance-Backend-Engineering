import 'package:flutter/material.dart';
import 'widgets/app_scaffold.dart';

class PackageTrackerApp extends StatelessWidget {
  const PackageTrackerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Package Tracker',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.indigo),
        useMaterial3: true,
      ),
      home: const AppScaffold(),
    );
  }
}
