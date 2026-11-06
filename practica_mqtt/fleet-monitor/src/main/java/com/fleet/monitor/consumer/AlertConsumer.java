package com.fleet.monitor.consumer;

import com.fleet.monitor.config.RabbitMQConfig;
import com.fleet.monitor.service.TelemetryService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.amqp.core.Message;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;

@Component
public class AlertConsumer {

    private static final Logger log = LoggerFactory.getLogger(AlertConsumer.class);

    private final RabbitTemplate rabbitTemplate;
    private final TelemetryService telemetryService;

    public AlertConsumer(RabbitTemplate rabbitTemplate, TelemetryService telemetryService) {
        this.rabbitTemplate = rabbitTemplate;
        this.telemetryService = telemetryService;
    }

    @RabbitListener(queues = RabbitMQConfig.TEMP_ALERT_QUEUE)
    public void consumeTempAlert(Message message) {
        String body = new String(message.getBody(), StandardCharsets.UTF_8);
        log.warn("ALERTA TEMPERATURA: {}", body);
        telemetryService.guardar("TEMPERATURA", body);
        // Reenvio a la cola de notificaciones (exchange por defecto, routing key = nombre de la cola)
        rabbitTemplate.convertAndSend(RabbitMQConfig.NOTIFICATION_QUEUE, body);
    }

    @RabbitListener(queues = RabbitMQConfig.FUEL_QUEUE)
    public void consumeFuelAlert(Message message) {
        String body = new String(message.getBody(), StandardCharsets.UTF_8);
        log.warn("ALERTA COMBUSTIBLE: {}", body);
        telemetryService.guardar("COMBUSTIBLE", body);
        rabbitTemplate.convertAndSend(RabbitMQConfig.NOTIFICATION_QUEUE, body);
    }
}
