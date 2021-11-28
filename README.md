# smart-garden

### Install micro-python on esp32
```bash
pip install esptool
# replace /dev/tty.SLAB_USBtoUART to proper port shows below
esptool.py --port /dev/tty.SLAB_USBtoUART erase_flash
esptool.py --chip esp32 --port /dev/tty.SLAB_USBtoUART write_flash -z 0x1000 esp32-20190930-v1.11-361-g4ba0aff47.bin
``` 


### Create kibana and elastisearch docker container
```bash
docker pull docker.elastic.co/kibana/kibana:7.4.0
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.4.0
docker volume create elasticsearch
docker volume create kibana
```

### Connect to the board using rshell or uPyCraft or ampy
```bash
pip install rshell adafruit-ampy
rshell -p /dev/cu.SLAB_USBtoUART

# For Mac OS 11 (big sur) run
pip install --upgrade  pyserial
rshell -p /dev/cu.usbserial-0001
cd esp/
cp * /pyboard
cd /pyboard

# only do this the first time when setup
ampy --port /dev/cu.SLAB_USBtoUART put configs /
# only do this the first time when setup

ampy --port /dev/cu.SLAB_USBtoUART put main.py main.py
ampy --port /dev/cu.SLAB_USBtoUART put start.py start.py
ampy --port /dev/cu.SLAB_USBtoUART put wifi_utils.py wifi_utils.py
ampy --port /dev/cu.SLAB_USBtoUART put boot.py boot.py
ampy --port /dev/cu.SLAB_USBtoUART put microWebSocket.py microWebSocket.py
ampy --port /dev/cu.SLAB_USBtoUART put microWebSrv.py microWebSrv.py
ampy --port /dev/cu.SLAB_USBtoUART put microWebTemplate.py microWebTemplate.py
ampy --port /dev/cu.SLAB_USBtoUART put ver.py ver.py
ampy --port /dev/cu.SLAB_USBtoUART put umqtt /
ampy --port /dev/cu.SLAB_USBtoUART put lib /
ampy --port /dev/cu.SLAB_USBtoUART put www /

```

### Run Code for testing
```
ampy --port /dev/cu.SLAB_USBtoUART run main.py
```
