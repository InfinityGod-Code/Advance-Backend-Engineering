package com.tracker.delivery_service.repository;

import com.tracker.delivery_service.entity.Delivery;
import com.tracker.delivery_service.entity.DeliveryStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface DeliveryRepository extends JpaRepository<Delivery, Long> {
    Optional<Delivery> findByDeliveryId(String deliveryId);
    Optional<Delivery> findByShipmentId(String shipmentId);
    boolean existsByShipmentId(String shipmentId);
    List<Delivery> findByStatus(DeliveryStatus status);
}
