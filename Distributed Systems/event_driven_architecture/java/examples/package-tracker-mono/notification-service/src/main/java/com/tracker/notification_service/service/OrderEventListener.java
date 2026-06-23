package com.tracker.notification_service.service;

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
public class OrderEventListener {

    private static final Logger log = LoggerFactory.getLogger(OrderEventListener.class);

    @KafkaListener(
            topics = "${app.kafka.topics.order-events:order-events}",
            containerFactory = "orderCreatedEventListenerFactory",
            groupId = "${spring.kafka.consumer.group-id:notification-service-group}"
    )
    public void onOrderCreated(
            @Payload OrderCreatedEvent event,
            @Header(KafkaHeaders.RECEIVED_KEY) String key,
            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
            @Header(KafkaHeaders.OFFSET) long offset,
            Acknowledgment ack) {

        log.info("Notification: Order created - orderId={}, customerId={}, amount={}",
                event.getOrderId(), event.getCustomerId(), event.getTotalAmount());

        try {
            sendOrderConfirmationEmail(event);
            ack.acknowledge();
            log.debug("Order notification acknowledged for orderId={}", event.getOrderId());
        } catch (Exception e) {
            log.error("Failed to process order notification for orderId={}: {}",
                    event.getOrderId(), e.getMessage(), e);
            throw e;
        }
    }

    private void sendOrderConfirmationEmail(OrderCreatedEvent event) {
        log.info("Sending order confirmation email to customer={} for order={}",
                event.getCustomerId(), event.getOrderId());
    }
}
