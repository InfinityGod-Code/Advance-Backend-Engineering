package com.tracker.common_events;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DeliveryStartedEvent {
    private String deliveryId;
    private String orderId;
    private String shipmentId;
    private String customerId;
    private long timestamp;
}
