package com.event_driven_learning_java.demo.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import java.time.LocalDate;

@Data
public class ShipmentRequest {
    @NotBlank(message = "Tracking number is required")
    private String trackingNumber;

    @NotBlank(message = "Origin is required")
    private String origin;

    @NotBlank(message = "Destination is required")
    private String destination;

    private Double weight;

    private LocalDate estimatedDelivery;

    @NotNull(message = "Seller ID is required")
    private Long sellerId;
}
