import paho.mqtt.client as mqtt

MQTT_BROKER = "192.168.1.100"  # Raspberry IP
MQTT_PORT = 1883

def kuld_home_assistant(topic, message):
    """Elküld egy MQTT üzenetet a Home Assistantnak."""
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.publish(topic, message)
    client.disconnect()