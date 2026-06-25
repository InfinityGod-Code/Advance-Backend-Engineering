package com.tracker.common_events;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ShipmentStartedEvent {
    private String orderId;
    private String shipmentId;
    private String customerId;
    private String status;
    private BigDecimal totalAmount;
    private String shippingStreet;
    private String shippingCity;
    private String shippingState;
    private String shippingZip;
    private long timestamp;
}
