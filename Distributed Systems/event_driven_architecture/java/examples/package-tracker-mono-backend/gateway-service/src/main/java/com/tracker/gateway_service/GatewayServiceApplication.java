package com.tracker.gateway_service;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
@EnableDiscoveryClient
public class GatewayServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(GatewayServiceApplication.class, args);
    }

    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
                // SSE stream route — no circuit breaker needed, long-lived connection
                .route("events-stream-java", r -> r
                        .path("/api/v1/events/stream", "/api/v1/events/stream/**")
                        .filters(f -> f.setResponseHeader("Cache-Control", "no-cache"))
                        .uri("lb://notification-service"))
                // Customer service — circuit breakers on all REST routes
                .route("customer-service", r -> r
                        .path("/api/v1/users/**", "/api/v1/orders/**")
                        .filters(f -> f.circuitBreaker(config -> config
                                .setName("customerServiceCB")
                                .setFallbackUri("forward:/fallback/customer-service")))
                        .uri("lb://customer-service"))
                // Shipment service
                .route("shipment-service", r -> r
                        .path("/api/v1/shipments/**")
                        .filters(f -> f.circuitBreaker(config -> config
                                .setName("shipmentServiceCB")
                                .setFallbackUri("forward:/fallback/shipment-service")))
                        .uri("lb://shipment-service"))
                // Delivery service
                .route("delivery-service", r -> r
                        .path("/api/v1/deliveries/**")
                        .filters(f -> f.circuitBreaker(config -> config
                                .setName("deliveryServiceCB")
                                .setFallbackUri("forward:/fallback/delivery-service")))
                        .uri("lb://delivery-service"))
                .build();
    }
}
