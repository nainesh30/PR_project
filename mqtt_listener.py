import json
import subprocess
import platform
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC_BROWSER_OPEN = "system/browser/open"


def open_edge(url: str):
    system = platform.system()

    if system == "Windows":
        subprocess.Popen(["cmd", "/c", "start", "msedge", url])

    elif system == "Linux":
        subprocess.Popen(["microsoft-edge", url])

    elif system == "Darwin":
        subprocess.Popen(["open", "-a", "Microsoft Edge", url])

    else:
        print("❌ Unsupported OS")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        if msg.topic == TOPIC_BROWSER_OPEN:
            if data.get("browser") == "edge":
                open_edge(data["url"])

    except Exception as e:
        print("⚠️ Error handling MQTT message:", e)


client = mqtt.Client()
client.on_message = on_message

client.connect(BROKER, PORT)
client.subscribe(TOPIC_BROWSER_OPEN)

print("📡 MQTT listener running...")
client.loop_forever()
