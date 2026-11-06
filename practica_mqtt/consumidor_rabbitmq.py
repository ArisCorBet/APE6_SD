import json
import pika

RABBITMQ_HOST = "localhost"

def procesar_mensaje(ch, method, properties, body):
    routing_key = method.routing_key
    payload = json.loads(body.decode("utf-8"))
    
    if routing_key == "cola.gps.telemetria":
        print(f"🌐 [GPS] Vehículo: {payload['vehicle_id']} | Lat: {payload['lat']}, Lng: {payload['lng']} | Vel: {payload['speed']} km/h")
    elif routing_key == "cola.alertas.temperatura":
        print(f"🔥 [ALERTA TEMP] {payload['vehicle_id']} -> Temperatura crítica: {payload['temperature']} °C")
    elif routing_key == "cola.combustible.nivel":
        print(f"⛽ [ALERTA COMBUSTIBLE] {payload['vehicle_id']} -> Nivel bajo: {payload['fuel_level']} %")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def principal():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    colas = ["cola.gps.telemetria", "cola.alertas.temperatura", "cola.combustible.nivel"]
    for cola in colas:
        channel.queue_declare(queue=cola, durable=True)
        channel.basic_consume(queue=cola, on_message_callback=procesar_mensaje)

    print("Escuchando mensajes en las colas de RabbitMQ...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nDeteniendo consumidor de RabbitMQ...")
        channel.stop_consuming()
        connection.close()

if __name__ == "__main__":
    principal()