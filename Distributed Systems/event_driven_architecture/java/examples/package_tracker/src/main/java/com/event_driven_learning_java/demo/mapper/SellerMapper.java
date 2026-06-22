package com.event_driven_learning_java.demo.mapper;

import com.event_driven_learning_java.demo.dto.SellerRequest;
import com.event_driven_learning_java.demo.dto.SellerResponse;
import com.event_driven_learning_java.demo.entity.Seller;

public class SellerMapper {

    public static Seller toEntity(SellerRequest request) {
        return Seller.builder()
                .name(request.getName())
                .email(request.getEmail())
                .phone(request.getPhone())
                .build();
    }

    public static SellerResponse toResponse(Seller seller) {
        SellerResponse response = new SellerResponse();
        response.setId(seller.getId());
        response.setName(seller.getName());
        response.setEmail(seller.getEmail());
        response.setPhone(seller.getPhone());
        response.setCreatedAt(seller.getCreatedAt());
        response.setUpdatedAt(seller.getUpdatedAt());
        return response;
    }

    public static void updateEntity(Seller seller, SellerRequest request) {
        seller.setName(request.getName());
        seller.setEmail(request.getEmail());
        seller.setPhone(request.getPhone());
    }
}
