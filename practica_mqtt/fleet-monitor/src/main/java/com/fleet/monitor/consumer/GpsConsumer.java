package com.fleet.monitor.consumer;

import com.fleet.monitor.config.RabbitMQConfig;
import com.fleet.monitor.service.TelemetryService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;

@Component
public class GpsConsumer {

    private static final Logger log = LoggerFactory.getLogger(GpsConsumer.class);

    private final TelemetryService telemetryService;

    public GpsConsumer(TelemetryService telemetryService) {
        this.telemetryService = telemetryService;
    }

    @RabbitListener(queues = RabbitMQConfig.GPS_QUEUE)
    public void consumeGps(Message message) {
        // Se leen los bytes directamente: pika (Python) publica sin content_type
        String body = new String(message.getBody(), StandardCharsets.UTF_8);
        try {
            log.info("GPS recibido: {}", body);
            telemetryService.guardar("GPS", body);
        } catch (Exception e) {
            log.error("Error procesando GPS: {}", e.getMessage());
        }
    }
}
