package com.event_driven_learning_java.demo.controllers.seller;

import com.event_driven_learning_java.demo.dto.SellerRequest;
import com.event_driven_learning_java.demo.dto.SellerResponse;
import com.event_driven_learning_java.demo.service.SellerService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/sellers")
@RequiredArgsConstructor
public class SellerController {

    private final SellerService sellerService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public SellerResponse create(@Valid @RequestBody SellerRequest request) {
        return sellerService.create(request);
    }

    @GetMapping
    public List<SellerResponse> findAll() {
        return sellerService.findAll();
    }

    @GetMapping("/{id}")
    public SellerResponse findById(@PathVariable Long id) {
        return sellerService.findById(id);
    }

    @PutMapping("/{id}")
    public SellerResponse update(@PathVariable Long id, @Valid @RequestBody SellerRequest request) {
        return sellerService.update(id, request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long id) {
        sellerService.delete(id);
    }
}
