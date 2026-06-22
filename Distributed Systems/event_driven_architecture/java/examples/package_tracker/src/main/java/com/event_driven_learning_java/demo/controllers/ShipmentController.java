package com.event_driven_learning_java.demo.controllers;

import com.event_driven_learning_java.demo.dto.ShipmentRequest;
import com.event_driven_learning_java.demo.dto.ShipmentResponse;
import com.event_driven_learning_java.demo.service.ShipmentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/shipments")
@RequiredArgsConstructor
public class ShipmentController {

    private final ShipmentService shipmentService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ShipmentResponse create(@Valid @RequestBody ShipmentRequest request) {
        return shipmentService.create(request);
    }
}
