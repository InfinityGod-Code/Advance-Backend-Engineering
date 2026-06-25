package com.tracker.delivery_service.controller;

import com.tracker.delivery_service.entity.Delivery;
import com.tracker.delivery_service.entity.DeliveryStatus;
import com.tracker.delivery_service.service.DeliveryService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/deliveries")
public class DeliveryController {

    private final DeliveryService deliveryService;

    public DeliveryController(DeliveryService deliveryService) {
        this.deliveryService = deliveryService;
    }

    @GetMapping
    public ResponseEntity<List<Delivery>> getAllDeliveries(
            @RequestParam(required = false) DeliveryStatus status) {
        return ResponseEntity.ok(deliveryService.getAllDeliveries(status));
    }

    @PostMapping("/{deliveryId}/approve")
    public ResponseEntity<Delivery> approveDelivery(@PathVariable String deliveryId) {
        return ResponseEntity.ok(deliveryService.approveDelivery(deliveryId));
    }

    @PostMapping("/{deliveryId}/delivered")
    public ResponseEntity<Delivery> markDelivered(@PathVariable String deliveryId) {
        return ResponseEntity.ok(deliveryService.markDelivered(deliveryId));
    }

    @PostMapping("/{deliveryId}/not-delivered")
    public ResponseEntity<Delivery> markNotDelivered(@PathVariable String deliveryId) {
        return ResponseEntity.ok(deliveryService.markNotDelivered(deliveryId));
    }
}
