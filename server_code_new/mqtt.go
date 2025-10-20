package main

import (
	"encoding/json"
	"fmt"
	"strconv"
	"strings"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	log "github.com/sirupsen/logrus"
)

type SensorJson struct {
	DeviceId     string  `json:"deviceId"`
	SoilMoisture string  `json:"soil_moist"`
	RawTemp      string  `json:"raw_temp"`
	AirHum       float64 `json:"air_hum"`
	AirTemp      float64 `json:"air_temp"`
	IpAddr       string  `json:"ip_addr"`
	DeviceName   string  `json:"device_name"`
}

var (
	defaultTopics = map[string]byte{
		// "topic/test": 0,
		// "+":             0,
		"sensor_data/+": 0,
	}

	subscribeOnConnect = func(client mqtt.Client) {
		log.Info("Broker Connected")
		log.Infof("Subscribing to topics: %v", defaultTopics)
		token := client.SubscribeMultiple(defaultTopics, func(client mqtt.Client, msg mqtt.Message) {
			log.Infof("Received message: %s from topic: %s\n", msg.Payload(), msg.Topic())
			topics := strings.Split(msg.Topic(), "/")
			deviceId := topics[len(topics)-1]
			sensorBody := SensorJson{
				DeviceId: deviceId,
			}
			err := json.Unmarshal(msg.Payload(), &sensorBody)
			if err != nil {
				log.Errorf("Failed to unmarshal message: %s", err)
				return
			}
			doc := ConvertSensorJonsToSensorDoc(sensorBody)
			err = esClient.AddSensorDoc(doc)
			if err != nil {
				log.Errorf("Failed to add sensor doc: %s", err)
			}
		})
		token.Wait()
	}
)

func ConvertSensorJonsToSensorDoc(sensorJson SensorJson) (doc SensorDoc) {
	doc = SensorDoc{
		DeviceId:   sensorJson.DeviceId,
		IpAddress:  sensorJson.IpAddr,
		RawTemp:    sensorJson.RawTemp,
		DeviceName: sensorJson.DeviceName,
	}
	doc.AirTemp = sensorJson.AirTemp
	doc.Moisture = ConvertRawMoistureFromAnalog(sensorJson.SoilMoisture)
	doc.SoilMoisture = strconv.FormatFloat(ConvertRawMoistureFromAnalog(sensorJson.SoilMoisture), 'f', 2, 64)
	doc.RawMoisture = sensorJson.SoilMoisture
	doc.AirHumidity = sensorJson.AirHum
	return doc
}

func NewMqttClients(conf Configs) (map[string]mqtt.Client, []error) {
	clientList := make(map[string]mqtt.Client)
	var errors []error
	for key, mqttServer := range conf.MqttServers {
		broker := mqttServer.MqttServer
		port := mqttServer.MqttPort
		opts := mqtt.NewClientOptions()
		opts.AddBroker(fmt.Sprintf("tcp://%s:%d", broker, port))
		opts.SetAutoReconnect(true)
		opts.OnConnect = subscribeOnConnect
		opts.OnConnectionLost = func(client mqtt.Client, err error) {
			log.Warningf("Connection lost for mqtt server %s: %s", key, err)
		}
		opts.OnReconnecting = func(client mqtt.Client, opts *mqtt.ClientOptions) {
			log.Warningf("Reconnecting for mqtt server %s", key)
		}
		if mqttServer.MqttUser != "" && mqttServer.MqttPass != "" {
			opts.SetUsername(mqttServer.MqttUser)
			opts.SetPassword(mqttServer.MqttPass)
		}
		client := mqtt.NewClient(opts)
		log.Infof("Connecting to broker %s:%d", broker, port)
		if token := client.Connect(); token.Wait() && token.Error() != nil {
			log.Errorf("Failed to connect to mqtt broker %s:%d: %s", broker, port, token.Error())
			errors = append(errors, token.Error())
			continue
		}
		clientList[key] = client
	}
	return clientList, errors
}
