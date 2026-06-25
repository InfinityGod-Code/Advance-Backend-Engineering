package com.tracker.gateway_service;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class GatewayServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(GatewayServiceApplication.class, args);
    }

    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
                .route("events-stream-java", r -> r
                        .path("/api/v1/events/stream", "/api/v1/events/stream/**")
                        .filters(f -> f.setResponseHeader("Cache-Control", "no-cache"))
                        .uri("http://notification-service:8080"))
                .route("customer-service", r -> r
                        .path("/api/v1/users/**", "/api/v1/orders/**")
                        .uri("http://customer-service:8080"))
                .route("shipment-service", r -> r
                        .path("/api/v1/shipments/**")
                        .uri("http://shipment-service:8080"))
                .route("delivery-service", r -> r
                        .path("/api/v1/deliveries/**")
                        .uri("http://delivery-service:8080"))
                .build();
    }
}
