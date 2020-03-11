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

### Connect to the board using rshell or uPyCraft
```bash
pip install rshell
rshell -p /dev/cu.SLAB_USBtoUART
```
cd /pyboard
