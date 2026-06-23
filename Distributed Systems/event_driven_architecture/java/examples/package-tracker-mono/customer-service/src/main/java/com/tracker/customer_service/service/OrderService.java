package com.tracker.customer_service.service;

import com.tracker.common_events.OrderCreatedEvent;
import com.tracker.customer_service.entity.Order;
import com.tracker.customer_service.entity.OrderStatus;
import com.tracker.customer_service.entity.User;
import com.tracker.customer_service.repository.OrderRepository;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.UUID;

@Service
public class OrderService {

    private static final String TOPIC = "order-events";

    private final OrderRepository orderRepository;
    private final UserService userService;
    private final KafkaTemplate<String, OrderCreatedEvent> kafkaTemplate;

    public OrderService(OrderRepository orderRepository,
                        UserService userService,
                        KafkaTemplate<String, OrderCreatedEvent> kafkaTemplate) {
        this.orderRepository = orderRepository;
        this.userService = userService;
        this.kafkaTemplate = kafkaTemplate;
    }

    public Order createOrder(Long userId, BigDecimal totalAmount) {
        User user = userService.getUserById(userId);

        Order order = Order.builder()
                .orderId("ORD-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase())
                .user(user)
                .status(OrderStatus.CREATED)
                .totalAmount(totalAmount)
                .shippingAddress(user.getAddress())
                .build();

        Order savedOrder = orderRepository.save(order);

        OrderCreatedEvent event = new OrderCreatedEvent(
                savedOrder.getOrderId(),
                String.valueOf(user.getId()),
                savedOrder.getTotalAmount(),
                System.currentTimeMillis()
        );

        kafkaTemplate.send(TOPIC, event.getOrderId(), event);

        return savedOrder;
    }
}
