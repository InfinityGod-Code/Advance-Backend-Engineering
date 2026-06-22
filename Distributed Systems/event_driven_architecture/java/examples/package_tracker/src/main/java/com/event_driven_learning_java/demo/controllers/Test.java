package com.event_driven_learning_java.demo.controllers;


import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/v1")
public class Test{

    @GetMapping("/hello")
    public Map<String, String> getHello(){
        Map<String,String> response = new HashMap<>();
        response.put("content","Hello World there  n nn n n nknkkn");
        return response;
    }
}