package com.event_driven_learning_java.demo.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class SellerResponse {
    private Long id;
    private String name;
    private String email;
    private String phone;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
