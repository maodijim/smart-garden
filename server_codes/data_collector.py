import paho.mqtt.client as mqtt
from elasticsearch import Elasticsearch
from datetime import datetime

mqtt_server = 'localhost'
elastic_server = 'localhost'


class DataPoint:
    def __init__(self):
        self.data = []
        self.data_time = []


es = Elasticsearch(hosts=[{"host": elastic_server, "port": 9200}])
# es.indices.create(index="soil-sensor", ignore=400)


def add_doc(msg):
    index = "soil-sensor"
    device_id = msg.topic.split('/')[0]
    body = {
        "device_id": device_id,
        "timestamp": datetime.utcnow()
    }
    if msg.topic.endswith('moist'):
        body['moisture'] = analog_to_percent(str(msg.payload.decode("utf-8")))
        body['raw_moist'] = str(msg.payload.decode("utf-8"))
    elif msg.topic.endswith('temp'):
        body['raw_temp'] = str(msg.payload.decode("utf-8"))
    es.index(index=index, body=body)


def on_log(client, userdata, level, buf):
    print("log: ", buf)


def on_message(client, userdata, message):
    global moist, temp, temp_plt, moist_plt, fig
    if message.topic.endswith('moist'):
        moist_reading = message.payload.decode("utf-8")
        print("message received ", str(moist_reading))
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)
        print(datetime.utcnow())
        if int(moist_reading) > 0:
            add_doc(message)
    elif message.topic.endswith('temp'):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        add_doc(message)


def analog_to_percent(analog):
    min_reading = 1750
    stepper = 35
    return 100 - (int(analog) - min_reading) / stepper

client = mqtt.Client('receiver')
client.connect(mqtt_server)
# client.on_log=on_log
client.on_message=on_message
client.subscribe("#")
client.loop_forever()