package com.event_driven_learning_java.demo.repository;

import com.event_driven_learning_java.demo.entity.Seller;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SellerRepository extends JpaRepository<Seller, Long> {
}
