package com.tracker.shipment_service.service;

import com.tracker.common_events.OrderCreatedEvent;
import com.tracker.common_events.ShipmentStartedEvent;
import com.tracker.shipment_service.entity.Shipment;
import com.tracker.shipment_service.entity.ShipmentStatus;
import com.tracker.shipment_service.repository.ShipmentRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class ShipmentService {

    private static final Logger log = LoggerFactory.getLogger(ShipmentService.class);

    private final ShipmentRepository shipmentRepository;
    private final KafkaTemplate<String, ShipmentStartedEvent> kafkaTemplate;

    @Value("${app.kafka.topics.shipment-events:shipment-events}")
    private String shipmentEventsTopic;

    public ShipmentService(ShipmentRepository shipmentRepository,
                           KafkaTemplate<String, ShipmentStartedEvent> kafkaTemplate) {
        this.shipmentRepository = shipmentRepository;
        this.kafkaTemplate = kafkaTemplate;
    }

    public void createShipment(OrderCreatedEvent event) {
        if (shipmentRepository.existsByOrderId(event.getOrderId())) {
            log.warn("Shipment already exists for orderId={}, skipping", event.getOrderId());
            shipmentRepository.findByOrderId(event.getOrderId()).orElseThrow();
            return;
        }

        Shipment shipment = Shipment.builder()
                .shipmentId("SHP-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase())
                .orderId(event.getOrderId())
                .customerId(event.getCustomerId())
                .status(ShipmentStatus.PENDING)
                .build();

        Shipment saved = shipmentRepository.save(shipment);
        log.info("Shipment created: id={}, orderId={}", saved.getShipmentId(), saved.getOrderId());

        ShipmentStartedEvent shipmentEvent = new ShipmentStartedEvent(
                saved.getShipmentId(),
                saved.getOrderId(),
                saved.getCustomerId(),
                System.currentTimeMillis()
        );

        kafkaTemplate.send(shipmentEventsTopic, shipmentEvent.getShipmentId(), shipmentEvent);
        log.info("ShipmentStartedEvent published: shipmentId={}, topic={}", shipmentEvent.getShipmentId(), shipmentEventsTopic);

    }
}
