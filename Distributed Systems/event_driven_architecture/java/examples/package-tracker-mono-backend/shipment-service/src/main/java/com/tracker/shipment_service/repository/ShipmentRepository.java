package com.tracker.shipment_service.repository;

import com.tracker.shipment_service.entity.Shipment;
import com.tracker.shipment_service.entity.ShipmentStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface ShipmentRepository extends JpaRepository<Shipment, Long> {
    Optional<Shipment> findByOrderId(String orderId);
    Optional<Shipment> findByShipmentId(String shipmentId);
    boolean existsByOrderId(String orderId);
    List<Shipment> findByStatus(ShipmentStatus status);
}
