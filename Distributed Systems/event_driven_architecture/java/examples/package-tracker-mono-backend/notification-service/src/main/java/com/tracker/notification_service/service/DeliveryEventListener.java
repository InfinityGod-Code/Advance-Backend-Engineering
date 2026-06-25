package com.tracker.notification_service.service;

import com.tracker.common_events.DeliveryStartedEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;

@Component
public class DeliveryEventListener {

    private static final Logger log = LoggerFactory.getLogger(DeliveryEventListener.class);
    private final SseEmitterService sseEmitterService;

    public DeliveryEventListener(SseEmitterService sseEmitterService) {
        this.sseEmitterService = sseEmitterService;
    }

    @KafkaListener(
            topics = "${app.kafka.topics.delivery-events:delivery-events}",
            containerFactory = "deliveryStartedEventListenerFactory",
            groupId = "${spring.kafka.consumer.group-id:notification-service-group}"
    )
    public void onDeliveryStarted(
            @Payload DeliveryStartedEvent event,
            @Header(KafkaHeaders.RECEIVED_KEY) String key,
            @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
            @Header(KafkaHeaders.OFFSET) long offset,
            Acknowledgment ack) {

        log.info("Notification: Delivery status - deliveryId={}, orderId={}, status={}, customerId={}",
                event.getDeliveryId(), event.getOrderId(), event.getStatus(), event.getCustomerId());

        try {
            sendDeliveryNotification(event);
            ack.acknowledge();
            sseEmitterService.broadcast("DeliveryStatusChanged", event);
            log.debug("Delivery notification acknowledged for deliveryId={}", event.getDeliveryId());
        } catch (Exception e) {
            log.error("Failed to process delivery notification for deliveryId={}: {}",
                    event.getDeliveryId(), e.getMessage(), e);
            throw e;
        }
    }

    private void sendDeliveryNotification(DeliveryStartedEvent event) {
        log.info("Sending delivery notification to customer={} for delivery={}, order={}, status={}",
                event.getCustomerId(), event.getDeliveryId(), event.getOrderId(), event.getStatus());
    }
}
