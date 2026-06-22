package com.event_driven_learning_java.demo.repository;

import com.event_driven_learning_java.demo.entity.Shipment;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ShipmentRepository extends JpaRepository<Shipment, Long> {
}
