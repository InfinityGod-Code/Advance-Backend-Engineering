package com.tracker.delivery_service.service;

import com.tracker.common_events.DeliveryStartedEvent;
import com.tracker.common_events.ShipmentStartedEvent;
import com.tracker.delivery_service.entity.Delivery;
import com.tracker.delivery_service.entity.DeliveryStatus;
import com.tracker.delivery_service.repository.DeliveryRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
public class DeliveryService {

    private static final Logger log = LoggerFactory.getLogger(DeliveryService.class);

    private final DeliveryRepository deliveryRepository;
    private final KafkaTemplate<String, DeliveryStartedEvent> kafkaTemplate;

    @Value("${app.kafka.topics.delivery-events:delivery-events}")
    private String deliveryEventsTopic;

    public DeliveryService(DeliveryRepository deliveryRepository,
                           KafkaTemplate<String, DeliveryStartedEvent> kafkaTemplate) {
        this.deliveryRepository = deliveryRepository;
        this.kafkaTemplate = kafkaTemplate;
    }

    @Transactional
    public Delivery createPendingDelivery(ShipmentStartedEvent event) {
        if (deliveryRepository.existsByShipmentId(event.getShipmentId())) {
            log.warn("Delivery already exists for shipmentId={}, skipping", event.getShipmentId());
            return deliveryRepository.findByShipmentId(event.getShipmentId()).orElseThrow();
        }

        Delivery delivery = Delivery.builder()
                .deliveryId("DEL-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase())
                .orderId(event.getOrderId())
                .shipmentId(event.getShipmentId())
                .customerId(event.getCustomerId())
                .totalAmount(event.getTotalAmount())
                .shippingStreet(event.getShippingStreet())
                .shippingCity(event.getShippingCity())
                .shippingState(event.getShippingState())
                .shippingZip(event.getShippingZip())
                .status(DeliveryStatus.PENDING_DELIVERY)
                .build();

        Delivery saved = deliveryRepository.save(delivery);
        log.info("Delivery pending agent approval: deliveryId={}, shipmentId={}",
                saved.getDeliveryId(), saved.getShipmentId());
        return saved;
    }

    @Transactional
    public Delivery approveDelivery(String deliveryId) {
        return updateDeliveryStatus(deliveryId, DeliveryStatus.OUT_FOR_DELIVERY);
    }

    @Transactional
    public Delivery markDelivered(String deliveryId) {
        return updateDeliveryStatus(deliveryId, DeliveryStatus.DELIVERED);
    }

    @Transactional
    public Delivery markNotDelivered(String deliveryId) {
        return updateDeliveryStatus(deliveryId, DeliveryStatus.NOT_DELIVERED);
    }

    private Delivery updateDeliveryStatus(String deliveryId, DeliveryStatus status) {
        Delivery delivery = getDelivery(deliveryId);
        delivery.setStatus(status);
        Delivery saved = deliveryRepository.save(delivery);
        publishDeliveryEvent(saved);
        log.info("Delivery status published: deliveryId={}, status={}, topic={}",
                deliveryId, status, deliveryEventsTopic);
        return saved;
    }

    public List<Delivery> getAllDeliveries(DeliveryStatus status) {
        if (status != null) {
            return deliveryRepository.findByStatus(status);
        }
        return deliveryRepository.findAll();
    }

    private Delivery getDelivery(String deliveryId) {
        return deliveryRepository.findByDeliveryId(deliveryId)
                .orElseThrow(() -> new RuntimeException("Delivery not found with id: " + deliveryId));
    }

    private void publishDeliveryEvent(Delivery delivery) {
        DeliveryStartedEvent deliveryEvent = DeliveryStartedEvent.builder()
                .deliveryId(delivery.getDeliveryId())
                .orderId(delivery.getOrderId())
                .shipmentId(delivery.getShipmentId())
                .customerId(delivery.getCustomerId())
                .status(delivery.getStatus().name())
                .totalAmount(delivery.getTotalAmount())
                .shippingStreet(delivery.getShippingStreet())
                .shippingCity(delivery.getShippingCity())
                .shippingState(delivery.getShippingState())
                .shippingZip(delivery.getShippingZip())
                .timestamp(System.currentTimeMillis())
                .build();

        kafkaTemplate.send(deliveryEventsTopic, deliveryEvent.getDeliveryId(), deliveryEvent);
    }
}
