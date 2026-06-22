package com.event_driven_learning_java.demo.service;

import com.event_driven_learning_java.demo.dto.SellerRequest;
import com.event_driven_learning_java.demo.dto.SellerResponse;
import com.event_driven_learning_java.demo.entity.Seller;
import com.event_driven_learning_java.demo.mapper.SellerMapper;
import com.event_driven_learning_java.demo.repository.SellerRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class SellerService {

    private final SellerRepository sellerRepository;

    @Transactional
    public SellerResponse create(SellerRequest request) {
        Seller seller = SellerMapper.toEntity(request);
        seller = sellerRepository.save(seller);
        return SellerMapper.toResponse(seller);
    }

    @Transactional(readOnly = true)
    public List<SellerResponse> findAll() {
        return sellerRepository.findAll().stream()
                .map(SellerMapper::toResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public SellerResponse findById(Long id) {
        Seller seller = sellerRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Seller not found with id: " + id));
        return SellerMapper.toResponse(seller);
    }

    @Transactional
    public SellerResponse update(Long id, SellerRequest request) {
        Seller seller = sellerRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Seller not found with id: " + id));
        SellerMapper.updateEntity(seller, request);
        seller = sellerRepository.save(seller);
        return SellerMapper.toResponse(seller);
    }

    @Transactional
    public void delete(Long id) {
        if (!sellerRepository.existsById(id)) {
            throw new EntityNotFoundException("Seller not found with id: " + id);
        }
        sellerRepository.deleteById(id);
    }
}
