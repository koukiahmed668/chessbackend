package com.kouki.chess.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

@RestController
@RequestMapping("/api/chess")
public class ChessController {

    @Value("${flask.api.url}")
    private String flaskApiUrl;

    private final RestTemplate restTemplate;

    public ChessController() {
        this.restTemplate = new RestTemplate();
    }

    @PostMapping("/move")
    public CompletableFuture<ResponseEntity<Map<String, String>>> makeMove(@RequestBody Map<String, String> request) {
        String fen = request.get("fen");

        if (fen == null || fen.isEmpty()) {
            return CompletableFuture.completedFuture(ResponseEntity.badRequest().body(Map.of("error", "FEN string is required")));
        }

        // Call the Flask API
        Map<String, String> flaskRequest = new HashMap<>();
        flaskRequest.put("fen", fen);

        return CompletableFuture.supplyAsync(() -> {
            ResponseEntity<Map> response = restTemplate.postForEntity(flaskApiUrl, flaskRequest, Map.class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                String move = (String) response.getBody().get("move");
                return ResponseEntity.ok(Map.of("move", move));
            } else {
                return ResponseEntity.status(response.getStatusCode()).body(Map.of("error", "Failed to get move from AI"));
            }
        });
    }
}
