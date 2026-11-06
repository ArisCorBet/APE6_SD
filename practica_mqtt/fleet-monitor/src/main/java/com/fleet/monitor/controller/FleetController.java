package com.fleet.monitor.controller;

import com.fleet.monitor.model.TelemetryRecord;
import com.fleet.monitor.repository.TelemetryRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/fleet")
public class FleetController {

    private final TelemetryRepository repository;

    public FleetController(TelemetryRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getFleetStatus() {
        Map<String, Object> status = new LinkedHashMap<>();
        status.put("totalVehicles", repository.contarVehiculos());
        status.put("activeAlerts", repository.countByTipoIn(List.of("TEMPERATURA", "COMBUSTIBLE")));
        status.put("totalMensajes", repository.count());
        status.put("timestamp", Instant.now());
        return ResponseEntity.ok(status);
    }

    @GetMapping("/vehicle/{id}/telemetria")
    public ResponseEntity<List<TelemetryRecord>> getTelemetria(@PathVariable String id) {
        return ResponseEntity.ok(repository.findByVehicleIdOrderByRecibidoEnDesc(id));
    }
}
