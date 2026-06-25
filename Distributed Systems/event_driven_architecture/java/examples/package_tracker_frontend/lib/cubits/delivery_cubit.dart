import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../models/delivery.dart';
import '../services/delivery_service.dart';

abstract class DeliveryState extends Equatable {
  const DeliveryState();
}

class DeliveryInitial extends DeliveryState {
  const DeliveryInitial();
  @override
  List<Object?> get props => [];
}

class DeliveryLoading extends DeliveryState {
  const DeliveryLoading();
  @override
  List<Object?> get props => [];
}

class DeliveryLoaded extends DeliveryState {
  final List<Delivery> deliveries;
  const DeliveryLoaded(this.deliveries);
  @override
  List<Object?> get props => [deliveries];
}

class DeliveryError extends DeliveryState {
  final String message;
  const DeliveryError(this.message);
  @override
  List<Object?> get props => [message];
}

class DeliveryCubit extends Cubit<DeliveryState> {
  final DeliveryService _service = DeliveryService();

  DeliveryCubit() : super(const DeliveryInitial());

  Future<void> loadDeliveries() async {
    emit(const DeliveryLoading());
    try {
      final deliveries = await _service.getDeliveries();
      emit(DeliveryLoaded(deliveries));
    } catch (e) {
      emit(DeliveryError('Failed to load deliveries: $e'));
    }
  }

  Future<void> approve(String deliveryId) async {
    try {
      await _service.approveDelivery(deliveryId);
      await loadDeliveries();
    } catch (e) {
      emit(DeliveryError('Failed to approve delivery: $e'));
    }
  }

  Future<void> delivered(String deliveryId) async {
    try {
      await _service.markDelivered(deliveryId);
      await loadDeliveries();
    } catch (e) {
      emit(DeliveryError('Failed to mark delivered: $e'));
    }
  }

  Future<void> notDelivered(String deliveryId) async {
    try {
      await _service.markNotDelivered(deliveryId);
      await loadDeliveries();
    } catch (e) {
      emit(DeliveryError('Failed to mark not delivered: $e'));
    }
  }
}
