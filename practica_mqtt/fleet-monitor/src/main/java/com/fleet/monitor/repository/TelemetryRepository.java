package com.fleet.monitor.repository;

import com.fleet.monitor.model.TelemetryRecord;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.Collection;
import java.util.List;

public interface TelemetryRepository extends JpaRepository<TelemetryRecord, Long> {

    List<TelemetryRecord> findByVehicleIdOrderByRecibidoEnDesc(String vehicleId);

    long countByTipoIn(Collection<String> tipos);

    @Query("select count(distinct t.vehicleId) from TelemetryRecord t")
    long contarVehiculos();
}
