package com.tracker.shipment_service.service;

import com.tracker.common_events.OrderCreatedEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;

@Component
public class OrderEventConsumer {

    private static final Logger log = LoggerFactory.getLogger(OrderEventConsumer.class);

    private final ShipmentService shipmentService;

    public OrderEventConsumer(ShipmentService shipmentService) {
        this.shipmentService = shipmentService;
    }

    @KafkaListener(
            topics = "${app.kafka.topics.order-events:order-events}",
            containerFactory = "orderCreatedEventListenerFactory",
            groupId = "${spring.kafka.consumer.group-id:shipment-service-group}"
    )
    public void onOrderCreated(
            @Payload OrderCreatedEvent event,
            @Header(KafkaHeaders.RECEIVED_KEY) String key,
            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
            @Header(KafkaHeaders.OFFSET) long offset,
            Acknowledgment ack) {

        log.info("Received OrderCreatedEvent: key={}, partition={}, offset={}, orderId={}, customerId={}",
                key, partition, offset, event.getOrderId(), event.getCustomerId());

        try {
            shipmentService.createShipment(event);
            ack.acknowledge();
            log.debug("Acknowledged offset={} for orderId={}", offset, event.getOrderId());
        } catch (Exception e) {
            log.error("Failed to process OrderCreatedEvent for orderId={}: {}", event.getOrderId(), e.getMessage(), e);
            throw e;
        }
    }
}
