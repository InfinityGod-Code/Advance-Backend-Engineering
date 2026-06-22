package com.event_driven_learning_java.demo.service;

import com.event_driven_learning_java.demo.dto.ShipmentRequest;
import com.event_driven_learning_java.demo.dto.ShipmentResponse;
import com.event_driven_learning_java.demo.entity.Seller;
import com.event_driven_learning_java.demo.entity.Shipment;
import com.event_driven_learning_java.demo.mapper.ShipmentMapper;
import com.event_driven_learning_java.demo.repository.SellerRepository;
import com.event_driven_learning_java.demo.repository.ShipmentRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ShipmentService {

    private final ShipmentRepository shipmentRepository;
    private final SellerRepository sellerRepository;

    @Transactional
    public ShipmentResponse create(ShipmentRequest request) {
        Seller seller = sellerRepository.findById(request.getSellerId())
                .orElseThrow(() -> new EntityNotFoundException("Seller not found with id: " + request.getSellerId()));

        Shipment shipment = ShipmentMapper.toEntity(request);
        shipment.setSeller(seller);
        shipment = shipmentRepository.save(shipment);
        return ShipmentMapper.toResponse(shipment);
    }
}
