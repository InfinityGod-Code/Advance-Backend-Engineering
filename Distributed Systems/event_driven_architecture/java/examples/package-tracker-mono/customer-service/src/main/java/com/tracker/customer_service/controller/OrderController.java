package com.tracker.customer_service.controller;

import com.tracker.customer_service.entity.Order;
import com.tracker.customer_service.service.OrderService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping
    public ResponseEntity<Order> createOrder(@RequestBody Map<String, Object> request) {
        Long userId = Long.valueOf(request.get("userId").toString());
        BigDecimal totalAmount = new BigDecimal(request.get("totalAmount").toString());
        Order order = orderService.createOrder(userId, totalAmount);
        return ResponseEntity.ok(order);
    }
}
