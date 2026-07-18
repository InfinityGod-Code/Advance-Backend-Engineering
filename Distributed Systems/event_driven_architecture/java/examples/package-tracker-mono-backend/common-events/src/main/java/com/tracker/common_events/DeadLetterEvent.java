package com.tracker.common_events;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DeadLetterEvent {
    private String originalTopic;
    private String originalKey;
    private String originalValue;
    private String consumerGroup;
    private String serviceName;
    private String errorType;
    private String errorMessage;
    private String stackTrace;
    private long failedAt;
    private int retryCount;
}
