import argparse
import logging
import os
import sys

import paho.mqtt.client as mqtt
from elasticsearch import Elasticsearch
from datetime import datetime
import configparser
import traceback
import json

from alert import AlertAction


class DataPoint:
    def __init__(self):
        self.data = []
        self.data_time = []


def add_doc(msg):
    """ Save sensor data to elasticsearch """
    if not msg.topic.startswith("sensor_data/"):
        return
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
    elif msg.topic.startswith('sensor_data'):
        body['device_id'] = msg.topic.split('/')[1]
        try:
            """ {"soil_moist": "", "raw_temp": "", "air_hum": "", "air_temp": "", "ip_addr": "", "device_name": ""} """
            result = json.loads(str(msg.payload.decode("utf-8")))
            body['moisture'] = analog_to_percent(result.get("soil_moist", 0))
            body['raw_moisture'] = result.get("soil_moist", 0)
            body['raw_temp'] = result.get("raw_temp", 0)
            body['air_humidity'] = result.get("air_hum", 0)
            body['air_temp'] = result.get("air_temp", 0)
            body['ip_address'] = result.get("ip_addr", '0.0.0.0')
            body['device_name'] = result.get("device_name", 'New Device')
        except:
            traceback.print_exc()
    else:
        try:
            """ {"soil_moist": "", "raw_temp": "", "air_hum": "", "air_temp": "", "ip_addr": ""} """
            result = json.loads(str(msg.payload.decode("utf-8")))
            body['moisture'] = analog_to_percent(result.get("soil_moist", 0))
            body['raw_moisture'] = result.get("soil_moist", 0)
            body['raw_temp'] = result.get("raw_temp", 0)
            body['air_humidity'] = result.get("air_hum", 0)
            body['air_temp'] = result.get("air_temp", 0)
            body['ip_address'] = result.get("ip_addr", '0.0.0.0')
        except:
            traceback.print_exc()
    try:
        es.index(index=configs['default']['index_name'], body=body)
    except:
        logging.error(traceback.format_exc())
    try:
        alerter.check_alert(body.get('device_id'), body.get("device_name", "Unknown Device"), body)
    except:
        logging.error(traceback.format_exc())


def on_log(client, userdata, level, buf):
    """ MQTT log handler """
    print("log: ", buf)


def on_message(client, userdata, message):
    """ MQTT message handler """
    global moist, temp, temp_plt, moist_plt, fig
    reading = message.payload.decode("utf-8")
    print("message received ", str(reading))
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)
    if message.topic.endswith('moist'):
        print(datetime.utcnow())
        if int(reading) > 0:
            add_doc(message)
    elif message.topic.endswith('temp'):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        add_doc(message)
    else:
        add_doc(message)


def analog_to_percent(analog):
    """ Convert raw reading from moisture sensor to percentage"""
    min_reading = 1750
    stepper = 32
    return 100 - (int(analog) - min_reading) / stepper


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

parser = argparse.ArgumentParser()
parser.add_argument("--config-path", help="Absolute path to the config file")
args = parser.parse_args()

configs = configparser.ConfigParser()
if args.config_path:
    configs.read(args.config_path)
else:
    configs.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'configs.conf'))

es = Elasticsearch(hosts=[{"host": configs['default']['elastic_server'],
                           "port": int(configs['default']['elastic_server_port'])}])
# es.indices.create(index="soil-sensor", ignore=400)

alerter = AlertAction(
    configs['email']['smtp_server'],
    configs['email']['email_username'],
    configs['email']['email_password'],
    configs['alert'],
    configs['email'],
    smtp_port=int(configs['email']['smtp_port'])
)

mqtt_client_name = "data_receiver"
if configs["default"].get("mqtt_client", "") != "":
    mqtt_client_name = configs["default"]["mqtt_client"]

client = mqtt.Client(mqtt_client_name)
username = configs['default'].get('mqtt_user', '')
user_pass = configs["default"].get("mqtt_pass", "")
if username != "" and user_pass != "":
    client.username_pw_set(username, user_pass)

client.connect(
    configs['default']['mqtt_server'],
    int(configs['default']['mqtt_port']),
)
client.on_log = on_log
client.on_message = on_message
client.subscribe([("+", 0), ("sensor_data/+", 0)])
client.loop_forever()