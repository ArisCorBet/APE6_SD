package com.fleet.monitor.model;

import jakarta.persistence.*;
import java.time.Instant;

@Entity
@Table(name = "telemetria")
public class TelemetryRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String vehicleId;

    // GPS, TEMPERATURA o COMBUSTIBLE
    private String tipo;

    // Mensaje original recibido desde RabbitMQ
    @Column(length = 4000)
    private String payload;

    private Instant recibidoEn;

    protected TelemetryRecord() { }

    public TelemetryRecord(String vehicleId, String tipo, String payload) {
        this.vehicleId = vehicleId;
        this.tipo = tipo;
        this.payload = payload;
        this.recibidoEn = Instant.now();
    }

    public Long getId() { return id; }
    public String getVehicleId() { return vehicleId; }
    public String getTipo() { return tipo; }
    public String getPayload() { return payload; }
    public Instant getRecibidoEn() { return recibidoEn; }
}
