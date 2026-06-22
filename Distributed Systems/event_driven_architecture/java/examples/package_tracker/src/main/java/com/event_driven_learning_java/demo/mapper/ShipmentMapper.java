package com.event_driven_learning_java.demo.mapper;

import com.event_driven_learning_java.demo.dto.ShipmentRequest;
import com.event_driven_learning_java.demo.dto.ShipmentResponse;
import com.event_driven_learning_java.demo.entity.Shipment;

public class ShipmentMapper {

    public static Shipment toEntity(ShipmentRequest request) {
        return Shipment.builder()
                .trackingNumber(request.getTrackingNumber())
                .origin(request.getOrigin())
                .destination(request.getDestination())
                .weight(request.getWeight())
                .estimatedDelivery(request.getEstimatedDelivery())
                .build();
    }

    public static ShipmentResponse toResponse(Shipment shipment) {
        ShipmentResponse response = new ShipmentResponse();
        response.setId(shipment.getId());
        response.setTrackingNumber(shipment.getTrackingNumber());
        response.setOrigin(shipment.getOrigin());
        response.setDestination(shipment.getDestination());
        response.setStatus(shipment.getStatus());
        response.setWeight(shipment.getWeight());
        response.setEstimatedDelivery(shipment.getEstimatedDelivery());
        response.setCreatedAt(shipment.getCreatedAt());
        response.setUpdatedAt(shipment.getUpdatedAt());
        response.setSellerId(shipment.getSeller().getId());
        return response;
    }
}
