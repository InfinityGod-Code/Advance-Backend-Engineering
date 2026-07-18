package com.tracker.notification_service.service;

import com.tracker.common_events.DeadLetterEvent;
import com.tracker.common_events.DeliveryStartedEvent;
import org.apache.kafka.common.errors.TimeoutException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.DataAccessException;
import org.springframework.kafka.annotation.BackOff;
import org.springframework.kafka.annotation.DltHandler;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.annotation.RetryableTopic;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.kafka.support.KafkaHeaders;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Component;

@Component
public class DeliveryEventListener {

    private static final Logger log = LoggerFactory.getLogger(DeliveryEventListener.class);

    private final SseEmitterService sseEmitterService;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    @Value("${app.kafka.topics.dead-letter-events:dead-letter-events}")
    private String deadLetterTopic;

    @Value("${spring.kafka.consumer.group-id:notification-service-group}")
    private String consumerGroup;

    @Value("${spring.application.name:notification-service}")
    private String serviceName;

    public DeliveryEventListener(SseEmitterService sseEmitterService,
                                 KafkaTemplate<String, Object> kafkaTemplate) {
        this.sseEmitterService = sseEmitterService;
        this.kafkaTemplate = kafkaTemplate;
    }

    @RetryableTopic(
            attempts = "4",
            backOff = @BackOff(delay = 1000, multiplier = 2.0),
            autoCreateTopics = "true",
            dltTopicSuffix = "-dlt",
            retryTopicSuffix = "-retry-{attempt}",
            include = {DataAccessException.class, TimeoutException.class},
            kafkaTemplate = "retryableTopicKafkaTemplate"
    )
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

        sendDeliveryNotification(event);
        sseEmitterService.broadcast("DeliveryStatusChanged", event);
        ack.acknowledge();
        log.debug("Delivery notification acknowledged for deliveryId={}", event.getDeliveryId());
    }

    @DltHandler
    public void onDltDeliveryStarted(
            @Payload DeliveryStartedEvent event,
            @Header(KafkaHeaders.RECEIVED_KEY) String key,
            @Header(KafkaHeaders.RECEIVED_TOPIC) String originalTopic,
            @Header(KafkaHeaders.OFFSET) long offset,
            @Header(value = "x-retry-count", defaultValue = "0") int retryCount,
            Acknowledgment ack) {

        log.error("DLT received for deliveryId={} from topic={} after {} retries. Event will be persisted for manual replay.",
                event.getDeliveryId(), originalTopic, retryCount);

        DeadLetterEvent dle = DeadLetterEvent.builder()
                .originalTopic(originalTopic)
                .originalKey(key)
                .originalValue(event.toString())
                .consumerGroup(consumerGroup)
                .serviceName(serviceName)
                .errorType("DataAccessException/TimeoutException")
                .errorMessage("Exhausted retries for deliveryId=" + event.getDeliveryId())
                .failedAt(System.currentTimeMillis())
                .retryCount(retryCount)
                .build();

        kafkaTemplate.send(deadLetterTopic, dle.getOriginalKey(), dle);
        ack.acknowledge();
    }

    private void sendDeliveryNotification(DeliveryStartedEvent event) {
        log.info("Sending delivery notification to customer={} for delivery={}, order={}, status={}",
                event.getCustomerId(), event.getDeliveryId(), event.getOrderId(), event.getStatus());
    }
}
