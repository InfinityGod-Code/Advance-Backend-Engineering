package com.tracker.shipment_service.repository;

import com.tracker.shipment_service.entity.Shipment;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ShipmentRepository extends JpaRepository<Shipment, Long> {
    Optional<Shipment> findByOrderId(String orderId);
    boolean existsByOrderId(String orderId);
}
