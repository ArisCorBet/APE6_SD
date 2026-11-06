package com.fleet.monitor.service;

import com.fleet.monitor.model.TelemetryRecord;
import com.fleet.monitor.repository.TelemetryRepository;
import org.springframework.stereotype.Service;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class TelemetryService {

    // Acepta los nombres de campo mas comunes para el ID del vehiculo
    private static final Pattern VEHICLE_ID = Pattern.compile(
        "\"(vehicle_id|vehiculo_id|vehicleId|vehiculoId|id_vehiculo|vehiculo)\"\\s*:\\s*\"?([^\",}\\s]+)");

    private final TelemetryRepository repository;

    public TelemetryService(TelemetryRepository repository) {
        this.repository = repository;
    }

    public TelemetryRecord guardar(String tipo, String payload) {
        return repository.save(new TelemetryRecord(extraerVehiculo(payload), tipo, payload));
    }

    private String extraerVehiculo(String payload) {
        Matcher m = VEHICLE_ID.matcher(payload);
        return m.find() ? m.group(2) : "DESCONOCIDO";
    }
}
