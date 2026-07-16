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
                .route("events-stream-java", r -> r
                        .path("/api/v1/events/stream", "/api/v1/events/stream/**")
                        .filters(f -> f.setResponseHeader("Cache-Control", "no-cache"))
                        .uri("lb://notification-service"))
                .route("customer-service", r -> r
                        .path("/api/v1/users/**", "/api/v1/orders/**")
                        .uri("lb://customer-service"))
                .route("shipment-service", r -> r
                        .path("/api/v1/shipments/**")
                        .uri("lb://shipment-service"))
                .route("delivery-service", r -> r
                        .path("/api/v1/deliveries/**")
                        .uri("lb://delivery-service"))
                .build();
    }
}
