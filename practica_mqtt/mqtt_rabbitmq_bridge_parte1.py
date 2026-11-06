import json
import pika
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
RABBITMQ_HOST = "localhost"

def configurar_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue="cola.gps.telemetria", durable=True)
    channel.queue_declare(queue="cola.alertas.temperatura", durable=True)
    channel.queue_declare(queue="cola.combustible.nivel", durable=True)
    print("Colas RabbitMQ declaradas exitosamente.")
    return connection, channel

def al_recibir_mensaje_mqtt(client, userdata, message):
    topic = message.topic
    payload = json.loads(message.payload.decode("utf-8"))
    channel = userdata["rabbitmq_channel"]

    if "/gps" in topic:
        channel.basic_publish(
            exchange='',
            routing_key='cola.gps.telemetria',
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )
    elif "/temperatura" in topic and payload.get("temperature", 0) > 4:
        alerta = {"type": "TEMP_ALERT", "message": "Temperatura excedida", **payload}
        channel.basic_publish(
            exchange='',
            routing_key='cola.alertas.temperatura',
            body=json.dumps(alerta),
            properties=pika.BasicProperties(delivery_mode=2)
        )
    elif "/combustible" in topic and payload.get("fuel_level", 100) < 20:
        alerta = {"type": "FUEL_LOW", "message": "Combustible bajo", **payload}
        channel.basic_publish(
            exchange='',
            routing_key='cola.combustible.nivel',
            body=json.dumps(alerta),
            properties=pika.BasicProperties(delivery_mode=2)
        )

def principal():
    conn_rabbit, canal_rabbit = configurar_rabbitmq()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata={"rabbitmq_channel": canal_rabbit})
    client.on_message = al_recibir_mensaje_mqtt
    
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe("flota/#")
    
    print("Bridge MQTT-RabbitMQ en ejecución...")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo Bridge Service...")
        client.disconnect()
        conn_rabbit.close()

if __name__ == "__main__":
    principal()
