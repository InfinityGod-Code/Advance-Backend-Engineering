package com.tracker.customer_service.service;

import com.tracker.common_events.OrderCreatedEvent;
import com.tracker.customer_service.controller.CreateOrderRequest;
import com.tracker.customer_service.entity.Address;
import com.tracker.customer_service.entity.Order;
import com.tracker.customer_service.entity.OrderStatus;
import com.tracker.customer_service.entity.User;
import com.tracker.customer_service.repository.OrderRepository;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

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

    public Order createOrder(CreateOrderRequest request) {
        User user = userService.getUserById(request.getUser().getId());

        String orderId = request.getOrderId() != null
                ? request.getOrderId()
                : "ORD-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase();

        OrderStatus status = request.getStatus() != null
                ? request.getStatus()
                : OrderStatus.CREATED;

        Address shippingAddress = request.getShippingAddress() != null
                ? request.getShippingAddress()
                : user.getAddress();

        Order order = Order.builder()
                .orderId(orderId)
                .user(user)
                .status(status)
                .totalAmount(request.getTotalAmount())
                .shippingAddress(shippingAddress)
                .build();

        Order savedOrder = orderRepository.save(order);

        Address savedAddress = savedOrder.getShippingAddress();
        OrderCreatedEvent event = OrderCreatedEvent.builder()
                .orderId(savedOrder.getOrderId())
                .customerId(String.valueOf(user.getId()))
                .totalAmount(savedOrder.getTotalAmount())
                .shippingStreet(savedAddress != null ? savedAddress.getStreet() : null)
                .shippingCity(savedAddress != null ? savedAddress.getCity() : null)
                .shippingState(savedAddress != null ? savedAddress.getState() : null)
                .shippingZip(savedAddress != null ? savedAddress.getZip() : null)
                .timestamp(System.currentTimeMillis())
                .build();

        kafkaTemplate.send(TOPIC, event.getOrderId(), event);

        return savedOrder;
    }
}
