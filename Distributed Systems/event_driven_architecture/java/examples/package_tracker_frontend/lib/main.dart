import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'app.dart';
import 'cubits/user_cubit.dart';
import 'cubits/order_cubit.dart';
import 'cubits/shipment_cubit.dart';
import 'cubits/delivery_cubit.dart';

void main() {
  runApp(
    MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => UserCubit()..loadUsers()),
        BlocProvider(create: (_) => OrderCubit()),
        BlocProvider(create: (_) => ShipmentCubit()..loadShipments()),
        BlocProvider(create: (_) => DeliveryCubit()..loadDeliveries()),
      ],
      child: const PackageTrackerApp(),
    ),
  );
}
