package com.tracker.notification_service.service;

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

    @KafkaListener(
            topics = "${app.kafka.topics.shipment-events:shipment-events}",
            containerFactory = "shipmentStartedEventListenerFactory",
            groupId = "${spring.kafka.consumer.group-id:notification-service-group}"
    )
    public void onShipmentStarted(
            @Payload ShipmentStartedEvent event,
            @Header(KafkaHeaders.RECEIVED_KEY) String key,
            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
            @Header(KafkaHeaders.OFFSET) long offset,
            Acknowledgment ack) {

        log.info("Notification: Shipment started - shipmentId={}, orderId={}, customerId={}",
                event.getShipmentId(), event.getOrderId(), event.getCustomerId());

        try {
            sendShipmentNotification(event);
            ack.acknowledge();
            log.debug("Shipment notification acknowledged for shipmentId={}", event.getShipmentId());
        } catch (Exception e) {
            log.error("Failed to process shipment notification for shipmentId={}: {}",
                    event.getShipmentId(), e.getMessage(), e);
            throw e;
        }
    }

    private void sendShipmentNotification(ShipmentStartedEvent event) {
        log.info("Sending shipment notification to customer={} for order={}, shipment={}",
                event.getCustomerId(), event.getOrderId(), event.getShipmentId());
    }
}
