package com.tracker.delivery_service.service;

import com.tracker.common_events.ShipmentStartedEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;

@Component
public class ShipmentEventListener {

    private static final Logger log = LoggerFactory.getLogger(ShipmentEventListener.class);

    private final DeliveryService deliveryService;

    public ShipmentEventListener(DeliveryService deliveryService) {
        this.deliveryService = deliveryService;
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

        log.info("Shipment event received for delivery: orderId={}, shipmentId={}, status={}, customerId={}",
                event.getOrderId(), event.getShipmentId(), event.getStatus(), event.getCustomerId());

        try {
            if ("SHIPPED".equals(event.getStatus())) {
                deliveryService.createPendingDelivery(event);
            } else {
                log.info("Ignoring non-shipped shipment event for delivery: shipmentId={}, status={}",
                        event.getShipmentId(), event.getStatus());
            }
            ack.acknowledge();
            log.debug("Shipment event acknowledged by delivery-service for shipmentId={}", event.getShipmentId());
        } catch (Exception e) {
            log.error("Failed to process delivery assignment for shipmentId={}: {}",
                    event.getShipmentId(), e.getMessage(), e);
            throw e;
        }
    }
}
