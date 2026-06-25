package com.tracker.shipment_service.controllers;

import com.tracker.shipment_service.entity.Shipment;
import com.tracker.shipment_service.entity.ShipmentStatus;
import com.tracker.shipment_service.service.ShipmentService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;


@RestController
@RequestMapping("/api/v1/shipments")
public class ShipmentController {

    private final ShipmentService shipmentService;

    public ShipmentController(ShipmentService shipmentService) {
        this.shipmentService = shipmentService;
    }

    @GetMapping
    public ResponseEntity<List<Shipment>> getAllShipments(
            @RequestParam(required = false) ShipmentStatus status) {
        return ResponseEntity.ok(shipmentService.getAllShipments(status));
    }

    @PostMapping("/{shipmentId}/approve")
    public ResponseEntity<Shipment> approveShipment(@PathVariable String shipmentId) {
        return ResponseEntity.ok(shipmentService.approveShipment(shipmentId));
    }

    @PostMapping("/{shipmentId}/decline")
    public ResponseEntity<Shipment> declineShipment(@PathVariable String shipmentId) {
        return ResponseEntity.ok(shipmentService.declineShipment(shipmentId));
    }
}
