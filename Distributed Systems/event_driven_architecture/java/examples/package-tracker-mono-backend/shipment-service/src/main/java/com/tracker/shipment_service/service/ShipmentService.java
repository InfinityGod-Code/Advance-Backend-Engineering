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
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
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

    @Transactional
    public Shipment createShipment(OrderCreatedEvent event) {
        if (shipmentRepository.existsByOrderId(event.getOrderId())) {
            log.warn("Shipment already exists for orderId={}, skipping", event.getOrderId());
            return shipmentRepository.findByOrderId(event.getOrderId()).orElseThrow();
        }

        Shipment shipment = Shipment.builder()
                .shipmentId("SHP-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase())
                .orderId(event.getOrderId())
                .customerId(event.getCustomerId())
                .totalAmount(event.getTotalAmount())
                .shippingStreet(event.getShippingStreet())
                .shippingCity(event.getShippingCity())
                .shippingState(event.getShippingState())
                .shippingZip(event.getShippingZip())
                .status(ShipmentStatus.PENDING_APPROVAL)
                .build();

        Shipment saved = shipmentRepository.save(shipment);
        log.info("Shipment pending approval: id={}, orderId={}", saved.getShipmentId(), saved.getOrderId());
        return saved;
    }

    @Transactional
    public Shipment approveShipment(String shipmentId) {
        Shipment shipment = getShipment(shipmentId);
        shipment.setStatus(ShipmentStatus.SHIPPED);
        Shipment saved = shipmentRepository.save(shipment);
        publishShipmentEvent(saved);
        log.info("Shipment approved and published: shipmentId={}, topic={}", shipmentId, shipmentEventsTopic);
        return saved;
    }

    @Transactional
    public Shipment declineShipment(String shipmentId) {
        Shipment shipment = getShipment(shipmentId);
        shipment.setStatus(ShipmentStatus.NOT_SHIPPED);
        Shipment saved = shipmentRepository.save(shipment);
        publishShipmentEvent(saved);
        log.info("Shipment declined and published: shipmentId={}, topic={}", shipmentId, shipmentEventsTopic);
        return saved;
    }

    public List<Shipment> getAllShipments(ShipmentStatus status) {
        if (status != null) {
            return shipmentRepository.findByStatus(status);
        }
        return shipmentRepository.findAll();
    }

    private Shipment getShipment(String shipmentId) {
        return shipmentRepository.findByShipmentId(shipmentId)
                .orElseThrow(() -> new RuntimeException("Shipment not found with id: " + shipmentId));
    }

    private void publishShipmentEvent(Shipment shipment) {
        ShipmentStartedEvent shipmentEvent = ShipmentStartedEvent.builder()
                .orderId(shipment.getOrderId())
                .shipmentId(shipment.getShipmentId())
                .customerId(shipment.getCustomerId())
                .status(shipment.getStatus().name())
                .totalAmount(shipment.getTotalAmount())
                .shippingStreet(shipment.getShippingStreet())
                .shippingCity(shipment.getShippingCity())
                .shippingState(shipment.getShippingState())
                .shippingZip(shipment.getShippingZip())
                .timestamp(System.currentTimeMillis())
                .build();

        kafkaTemplate.send(shipmentEventsTopic, shipmentEvent.getShipmentId(), shipmentEvent);
    }
}
