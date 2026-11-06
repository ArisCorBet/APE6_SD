import json
import sqlite3
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883

def inicializar_base_datos():
    conn = sqlite3.connect("telemetria.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gps_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT, lat REAL, lng REAL, speed REAL, timestamp TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temp_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT, temperature REAL, unit TEXT, timestamp TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fuel_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT, fuel_level REAL, unit TEXT, timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")

def al_recibir_mensaje(client, userdata, message):
    topic = message.topic
    payload = json.loads(message.payload.decode("utf-8"))
    conn = sqlite3.connect("telemetria.db")
    cursor = conn.cursor()

    if "/gps" in topic:
        cursor.execute(
            "INSERT INTO gps_data (vehicle_id, lat, lng, speed, timestamp) VALUES (?, ?, ?, ?, ?)",
            (payload["vehicle_id"], payload["lat"], payload["lng"], payload["speed"], payload["timestamp"])
        )
    elif "/temperatura" in topic:
        temp = payload["temperature"]
        if temp > 4:
            print(f"  ALERTA TEMPERATURA: {payload['vehicle_id']} registró {temp} °C")
        cursor.execute(
            "INSERT INTO temp_data (vehicle_id, temperature, unit, timestamp) VALUES (?, ?, ?, ?)",
            (payload["vehicle_id"], payload["temperature"], payload["unit"], payload["timestamp"])
        )
    elif "/combustible" in topic:
        fuel = payload["fuel_level"]
        if fuel < 20:
            print(f" ALERTA COMBUSTIBLE: {payload['vehicle_id']} nivel bajo: {fuel} %")
        cursor.execute(
            "INSERT INTO fuel_data (vehicle_id, fuel_level, unit, timestamp) VALUES (?, ?, ?, ?)",
            (payload["vehicle_id"], payload["fuel_level"], payload["unit"], payload["timestamp"])
        )

    conn.commit()
    conn.close()

def principal():
    inicializar_base_datos()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = al_recibir_mensaje
    client.connect(BROKER, PORT)
    
    client.subscribe("flota/+/gps")
    client.subscribe("flota/+/temperatura")
    client.subscribe("flota/+/combustible")

    print("Suscriptor activo. Escuchando topics flota/+/...")
    client.loop_forever()

if __name__ == "__main__":
    principal()
