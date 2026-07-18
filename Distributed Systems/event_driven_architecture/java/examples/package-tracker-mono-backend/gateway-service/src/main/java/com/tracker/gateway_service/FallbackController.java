package com.tracker.gateway_service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

import java.util.Map;

/**
 * Fallback controller for the circuit breaker pattern.
 * Each backend service gets its own fallback endpoint.
 * When a downstream service is unhealthy, the gateway circuit breaker
 * triggers and returns a structured 503 response instead of hanging
 * or returning a generic gateway timeout.
 */
@RestController
public class FallbackController {

    private static final Logger log = LoggerFactory.getLogger(FallbackController.class);

    @GetMapping("/fallback/customer-service")
    public Mono<Map<String, Object>> customerServiceFallback() {
        log.warn("Circuit breaker triggered for customer-service — returning 503 fallback");
        return Mono.just(Map.of(
                "status", HttpStatus.SERVICE_UNAVAILABLE.value(),
                "error", "Service Unavailable",
                "message", "customer-service is temporarily unavailable. Please try again later."
        ));
    }

    @GetMapping("/fallback/shipment-service")
    public Mono<Map<String, Object>> shipmentServiceFallback() {
        log.warn("Circuit breaker triggered for shipment-service — returning 503 fallback");
        return Mono.just(Map.of(
                "status", HttpStatus.SERVICE_UNAVAILABLE.value(),
                "error", "Service Unavailable",
                "message", "shipment-service is temporarily unavailable. Please try again later."
        ));
    }

    @GetMapping("/fallback/delivery-service")
    public Mono<Map<String, Object>> deliveryServiceFallback() {
        log.warn("Circuit breaker triggered for delivery-service — returning 503 fallback");
        return Mono.just(Map.of(
                "status", HttpStatus.SERVICE_UNAVAILABLE.value(),
                "error", "Service Unavailable",
                "message", "delivery-service is temporarily unavailable. Please try again later."
        ));
    }
}
