import json
import os
import pika
import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = 1883
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin123")

# Misma topologia que RabbitMQConfig.java (Parte 2)
EXCHANGE = "exchange.fleet"
BINDINGS = {
    "cola.gps.telemetria": "gps.routing",
    "cola.alertas.temperatura": "temp.alert",
    "cola.combustible.nivel": "fuel.routing",
}

def configurar_rabbitmq():
    credenciales = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credenciales))
    channel = connection.channel()
    # Declaraciones idempotentes: si ya existen con la misma configuracion, no pasa nada
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    for cola, routing_key in BINDINGS.items():
        channel.queue_declare(queue=cola, durable=True)
        channel.queue_bind(queue=cola, exchange=EXCHANGE, routing_key=routing_key)
    print(f"Exchange '{EXCHANGE}', colas y bindings listos en {RABBITMQ_HOST}.")
    return connection, channel

def publicar(channel, routing_key, datos):
    channel.basic_publish(
        exchange=EXCHANGE,
        routing_key=routing_key,
        body=json.dumps(datos),
        properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"))
    print(f"  -> {EXCHANGE} [{routing_key}] {datos.get('vehicle_id')}")

def al_recibir_mensaje_mqtt(client, userdata, message):
    topic = message.topic
    try:
        payload = json.loads(message.payload.decode("utf-8"))
    except json.JSONDecodeError:
        print(f"Mensaje no JSON ignorado en {topic}")
        return
    channel = userdata["rabbitmq_channel"]

    if topic.endswith("/gps"):
        publicar(channel, "gps.routing", payload)
    elif topic.endswith("/temperatura") and payload.get("temperature", 0) > 4:
        alerta = {"type": "TEMP_ALERT", "message": "Temperatura excedida", **payload}
        publicar(channel, "temp.alert", alerta)
    elif topic.endswith("/combustible") and payload.get("fuel_level", 100) < 20:
        alerta = {"type": "FUEL_LOW", "message": "Combustible bajo", **payload}
        publicar(channel, "fuel.routing", alerta)

def principal():
    conn_rabbit, canal_rabbit = configurar_rabbitmq()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         userdata={"rabbitmq_channel": canal_rabbit})
    client.on_message = al_recibir_mensaje_mqtt

    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe("flota/#")

    print(f"Bridge MQTT ({MQTT_BROKER}) -> RabbitMQ ({RABBITMQ_HOST}) en ejecucion...")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo Bridge Service...")
        client.disconnect()
        conn_rabbit.close()

if __name__ == "__main__":
    principal()
