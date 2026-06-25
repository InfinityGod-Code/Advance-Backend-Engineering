import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../models/shipment.dart';
import '../services/shipment_service.dart';

abstract class ShipmentState extends Equatable {
  const ShipmentState();
}

class ShipmentInitial extends ShipmentState {
  const ShipmentInitial();
  @override
  List<Object?> get props => [];
}

class ShipmentLoading extends ShipmentState {
  const ShipmentLoading();
  @override
  List<Object?> get props => [];
}

class ShipmentLoaded extends ShipmentState {
  final List<Shipment> shipments;
  const ShipmentLoaded(this.shipments);
  @override
  List<Object?> get props => [shipments];
}

class ShipmentError extends ShipmentState {
  final String message;
  const ShipmentError(this.message);
  @override
  List<Object?> get props => [message];
}

class ShipmentCubit extends Cubit<ShipmentState> {
  final ShipmentService _service = ShipmentService();

  ShipmentCubit() : super(const ShipmentInitial());

  Future<void> loadShipments() async {
    emit(const ShipmentLoading());
    try {
      final shipments = await _service.getShipments();
      emit(ShipmentLoaded(shipments));
    } catch (e) {
      emit(ShipmentError('Failed to load shipments: $e'));
    }
  }

  Future<void> approve(String shipmentId) async {
    try {
      await _service.approveShipment(shipmentId);
      await loadShipments();
    } catch (e) {
      emit(ShipmentError('Failed to approve shipment: $e'));
    }
  }

  Future<void> decline(String shipmentId) async {
    try {
      await _service.declineShipment(shipmentId);
      await loadShipments();
    } catch (e) {
      emit(ShipmentError('Failed to decline shipment: $e'));
    }
  }
}
