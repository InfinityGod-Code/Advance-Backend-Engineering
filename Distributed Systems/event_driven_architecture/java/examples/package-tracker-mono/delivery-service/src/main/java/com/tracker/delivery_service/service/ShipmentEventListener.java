package com.tracker.delivery_service.service;

import com.tracker.common_events.DeliveryStartedEvent;
import com.tracker.common_events.ShipmentStartedEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Component
public class ShipmentEventListener {

    private static final Logger log = LoggerFactory.getLogger(ShipmentEventListener.class);

    private final KafkaTemplate<String, DeliveryStartedEvent> kafkaTemplate;

    @Value("${app.kafka.topics.delivery-events:delivery-events}")
    private String deliveryEventsTopic;

    public ShipmentEventListener(KafkaTemplate<String, DeliveryStartedEvent> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    @KafkaListener(
            topics = "${app.kafka.topics.shipment-events:shipment-events}",
            containerFactory = "shipmentStartedEventListenerFactory",
            groupId = "${spring.kafka.consumer.group-id:delivery-service-group}"
    )
    public void onShipmentStarted(
            @Payload ShipmentStartedEvent event,
            @Header(KafkaHeaders.RECEIVED_KEY) String key,
            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
            @Header(KafkaHeaders.OFFSET) long offset,
            Acknowledgment ack) {

        log.info("Delivery assigned: orderId={}, shipmentId={}, customerId={}",
                event.getOrderId(), event.getShipmentId(), event.getCustomerId());

        try {
            assignDelivery(event);
            publishDeliveryEvent(event);
            ack.acknowledge();
            log.debug("Delivery assignment acknowledged for shipmentId={}", event.getShipmentId());
        } catch (Exception e) {
            log.error("Failed to process delivery assignment for shipmentId={}: {}",
                    event.getShipmentId(), e.getMessage(), e);
            throw e;
        }
    }

    private void assignDelivery(ShipmentStartedEvent event) {
        log.info("Routing delivery personnel to customer={} for order={}, shipment={}",
                event.getCustomerId(), event.getOrderId(), event.getShipmentId());
    }

    private void publishDeliveryEvent(ShipmentStartedEvent event) {
        DeliveryStartedEvent deliveryEvent = new DeliveryStartedEvent(
                "DEL-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase(),
                event.getOrderId(),
                event.getShipmentId(),
                event.getCustomerId(),
                System.currentTimeMillis()
        );
        kafkaTemplate.send(deliveryEventsTopic, deliveryEvent.getDeliveryId(), deliveryEvent);
        log.info("DeliveryStartedEvent published: deliveryId={}, topic={}",
                deliveryEvent.getDeliveryId(), deliveryEventsTopic);
    }
}
