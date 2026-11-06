import json
import time
import random
import datetime
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
VEHICULOS = ["VH-001", "VH-002", "VH-003"]

def on_connect(client, userdata, flags, rc, properties=None):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Conectado al broker MQTT (rc={rc})")

def simular_gps(id_vehiculo):
    base_lat = -2.1709
    base_lng = -79.9224
    return {
        "lat": round(base_lat + random.uniform(-0.01, 0.01), 6),
        "lng": round(base_lng + random.uniform(-0.01, 0.01), 6),
        "speed": round(random.uniform(20, 80), 1)
    }

def simular_temperatura(id_vehiculo):
    return {
        "temperature": round(random.uniform(-5, 8), 1),
        "unit": "celsius"
    }

def simular_combustible(id_vehiculo):
    return {
        "fuel_level": round(random.uniform(10, 100), 1),
        "unit": "percent"
    }

def principal():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(BROKER, PORT)
    client.loop_start()

    print("Iniciando simulador de sensores IoT...")
    try:
        while True:
            for vehiculo in VEHICULOS:
                timestamp = datetime.datetime.now().isoformat()

                # GPS
                datos_gps = {"vehicle_id": vehiculo, "timestamp": timestamp, **simular_gps(vehiculo)}
                client.publish(f"flota/{vehiculo}/gps", json.dumps(datos_gps))

                # Temperatura
                datos_temp = {"vehicle_id": vehiculo, "timestamp": timestamp, **simular_temperatura(vehiculo)}
                client.publish(f"flota/{vehiculo}/temperatura", json.dumps(datos_temp))

                # Combustible
                datos_fuel = {"vehicle_id": vehiculo, "timestamp": timestamp, **simular_combustible(vehiculo)}
                client.publish(f"flota/{vehiculo}/combustible", json.dumps(datos_fuel))

                print(f"[{timestamp}] Datos publicados para {vehiculo}")
                time.sleep(5)
    except KeyboardInterrupt:
        print("\nDeteniendo simulador...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    principal()
