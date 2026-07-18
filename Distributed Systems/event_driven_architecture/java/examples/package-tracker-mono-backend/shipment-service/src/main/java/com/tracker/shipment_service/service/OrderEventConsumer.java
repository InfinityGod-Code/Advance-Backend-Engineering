package com.tracker.shipment_service.service;

import com.tracker.common_events.DeadLetterEvent;
import com.tracker.common_events.OrderCreatedEvent;
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
public class OrderEventConsumer {

    private static final Logger log = LoggerFactory.getLogger(OrderEventConsumer.class);

    private final ShipmentService shipmentService;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    @Value("${app.kafka.topics.dead-letter-events:dead-letter-events}")
    private String deadLetterTopic;

    @Value("${spring.kafka.consumer.group-id:shipment-service-group}")
    private String consumerGroup;

    @Value("${spring.application.name:shipment-service}")
    private String serviceName;

    public OrderEventConsumer(ShipmentService shipmentService,
                              KafkaTemplate<String, Object> kafkaTemplate) {
        this.shipmentService = shipmentService;
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

        shipmentService.createShipment(event);
        ack.acknowledge();
        log.debug("Acknowledged offset={} for orderId={}", offset, event.getOrderId());
    }

    @DltHandler
    public void onDltOrderCreated(
            @Payload OrderCreatedEvent event,
            @Header(KafkaHeaders.RECEIVED_KEY) String key,
            @Header(KafkaHeaders.RECEIVED_TOPIC) String originalTopic,
            @Header(KafkaHeaders.OFFSET) long offset,
            @Header(value = "x-retry-count", defaultValue = "0") int retryCount,
            Acknowledgment ack) {

        log.error("DLT received for orderId={} from topic={} after {} retries. Event will be persisted for manual replay.",
                event.getOrderId(), originalTopic, retryCount);

        DeadLetterEvent dle = DeadLetterEvent.builder()
                .originalTopic(originalTopic)
                .originalKey(key)
                .originalValue(event.toString())
                .consumerGroup(consumerGroup)
                .serviceName(serviceName)
                .errorType("DataAccessException/TimeoutException")
                .errorMessage("Exhausted retries for orderId=" + event.getOrderId())
                .failedAt(System.currentTimeMillis())
                .retryCount(retryCount)
                .build();

        kafkaTemplate.send(deadLetterTopic, dle.getOriginalKey(), dle);
        ack.acknowledge();
    }
}
