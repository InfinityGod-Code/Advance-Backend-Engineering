package com.event_driven_learning_java.demo.dto;

import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class ShipmentResponse {
    private Long id;
    private String trackingNumber;
    private String origin;
    private String destination;
    private String status;
    private Double weight;
    private LocalDate estimatedDelivery;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private Long sellerId;
}
