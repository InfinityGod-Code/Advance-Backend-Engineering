package com.tracker.delivery_service.service;

import com.tracker.common_events.DeadLetterEvent;
import com.tracker.common_events.ShipmentStartedEvent;
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
public class ShipmentEventListener {

    private static final Logger log = LoggerFactory.getLogger(ShipmentEventListener.class);

    private final DeliveryService deliveryService;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    @Value("${app.kafka.topics.dead-letter-events:dead-letter-events}")
    private String deadLetterTopic;

    @Value("${spring.kafka.consumer.group-id:delivery-service-group}")
    private String consumerGroup;

    @Value("${spring.application.name:delivery-service}")
    private String serviceName;

    public ShipmentEventListener(DeliveryService deliveryService,
                                 KafkaTemplate<String, Object> kafkaTemplate) {
        this.deliveryService = deliveryService;
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

        if ("SHIPPED".equals(event.getStatus())) {
            deliveryService.createPendingDelivery(event);
        } else {
            log.info("Ignoring non-shipped shipment event for delivery: shipmentId={}, status={}",
                    event.getShipmentId(), event.getStatus());
        }
        ack.acknowledge();
        log.debug("Shipment event acknowledged by delivery-service for shipmentId={}", event.getShipmentId());
    }

    @DltHandler
    public void onDltShipmentStarted(
            @Payload ShipmentStartedEvent event,
            @Header(KafkaHeaders.RECEIVED_KEY) String key,
            @Header(KafkaHeaders.RECEIVED_TOPIC) String originalTopic,
            @Header(KafkaHeaders.OFFSET) long offset,
            @Header(value = "x-retry-count", defaultValue = "0") int retryCount,
            Acknowledgment ack) {

        log.error("DLT received for shipmentId={} from topic={} after {} retries. Event will be persisted for manual replay.",
                event.getShipmentId(), originalTopic, retryCount);

        DeadLetterEvent dle = DeadLetterEvent.builder()
                .originalTopic(originalTopic)
                .originalKey(key)
                .originalValue(event.toString())
                .consumerGroup(consumerGroup)
                .serviceName(serviceName)
                .errorType("DataAccessException/TimeoutException")
                .errorMessage("Exhausted retries for shipmentId=" + event.getShipmentId())
                .failedAt(System.currentTimeMillis())
                .retryCount(retryCount)
                .build();

        kafkaTemplate.send(deadLetterTopic, dle.getOriginalKey(), dle);
        ack.acknowledge();
    }
}
