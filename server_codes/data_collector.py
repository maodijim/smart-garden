import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy
import time
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import pickle
import os

class DataPoint:
    def __init__(self):
        self.data = []
        self.data_time = []


pickle_t_file = 'datapoint-temp1.pkl'
pickle_m_file = 'datapoint-moist1.pkl'
temp = DataPoint()
moist = DataPoint()
myFmt = mdates.DateFormatter('%H:%M:%S')

if os.path.exists(pickle_t_file):
    temp = pickle.load(open(pickle_t_file, 'rb'))
if os.path.exists(pickle_m_file):
    moist = pickle.load(open(pickle_m_file, 'rb'))

fig = plt.figure()

ax1 = fig.add_subplot(211)
moist_plt, = ax1.plot(moist.data_time, moist.data)

ax2 = fig.add_subplot(212)
temp_plt, = ax2.plot(temp.data_time, temp.data)

ax1.xaxis.set_major_formatter(myFmt)
ax2.xaxis.set_major_formatter(myFmt)
plt.gcf().autofmt_xdate()
plt.gcf().autofmt_xdate()
try:
    plt.show()
except Exception as e:
    print(e)
    pass

es = Elasticsearch(hosts=[{"host": "andy-nas.local", "port": 9200}])
# es.indices.create(index="soil-sensor")

def add_doc(msg):
    index = "soil-sensor"
    device_id = msg.topic.split('/')[0]
    body = {
        "device_id": device_id,
        "timestamp": datetime.now()
    }
    if msg.topic.endswith('moist'):
        body['moisture'] =str(msg.payload.decode("utf-8"))
    elif msg.topic.endswith('temp'):
        body['raw_temp'] = str(msg.payload.decode("utf-8"))
    es.index(index=index, body=body)

def on_log(client, userdata, level, buf):
    print("log: ",buf)


def on_message(client, userdata, message):
    global moist, temp, temp_plt, moist_plt, fig
    if message.topic.endswith('moist'):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)
        print(datetime.now())
        moist.data.append(str(message.payload.decode("utf-8")))
        moist.data_time.append(datetime.now())
        pickle.dump(moist, open(pickle_m_file, 'wb'))
        add_doc(message)
        # moist_plt.set_ydata(numpy.append(moist_plt.get_ydata(), str(message.payload.decode("utf-8"))))
    elif message.topic.endswith('temp'):
        print("message received ", str(message.payload.decode("utf-8")))
        print("message topic=", message.topic)
        temp.data.append(str(message.payload.decode("utf-8")))
        temp.data_time.append(datetime.now())
        pickle.dump(temp, open(pickle_t_file, 'wb'))
        add_doc(message)
        # temp_plt.set_ydata(numpy.append(temp_plt.get_ydata(), str(message.payload.decode("utf-8"))))
    # print(temp_plt.get_ydata())
    # print(moist_plt.get_ydata())
    fig.canvas.draw()


client = mqtt.Client('receiver')
client.connect('andy-nas.local')
# client.on_log=on_log
client.on_message=on_message
# client.loop_start()
print("Subscribing to topic","house/bulbs/bulb1")
client.subscribe("#")
# client.publish("test", "sdf")
# time.sleep(4)
# client.loop_stop()
client.loop_forever()
# plt.show()
