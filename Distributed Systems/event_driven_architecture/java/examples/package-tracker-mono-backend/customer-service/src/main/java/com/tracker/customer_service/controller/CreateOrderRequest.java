package com.tracker.customer_service.controller;

import com.tracker.customer_service.entity.Address;
import com.tracker.customer_service.entity.OrderStatus;
import lombok.Data;

import java.math.BigDecimal;

@Data
public class CreateOrderRequest {
    private String orderId;
    private UserRef user;
    private OrderStatus status;
    private BigDecimal totalAmount;
    private Address shippingAddress;

    @Data
    public static class UserRef {
        private Long id;
    }
}
