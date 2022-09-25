package main

import (
	"context"
	"strconv"
	"strings"
	"time"

	"github.com/olivere/elastic/v7"
	log "github.com/sirupsen/logrus"
)

var (
	r map[string]interface{}
)

type SensorDoc struct {
	DeviceId     string    `json:"device_id"`
	Moisture     float64   `json:"moisture"`
	SoilMoisture string    `json:"soil_moisture"`
	AirHumidity  float64   `json:"air_humidity"`
	AirTemp      float64   `json:"air_temp"`
	DeviceName   string    `json:"device_name"`
	IpAddress    string    `json:"ip_address"`
	RawMoisture  string    `json:"raw_moisture"`
	RawTemp      string    `json:"raw_temp"`
	Timestamp    time.Time `json:"timestamp"`
}

func ConvertRawMoistureFromAnalog(rawMoisture string) float64 {
	minReading := float64(1750)
	stepper := float64(32)
	raw, err := strconv.ParseFloat(rawMoisture, 32)
	if err != nil {
		log.Errorf("failed to convert raw moisture: %s", err)
		raw = 0
	}
	return 100 - (raw-minReading)/stepper
}

type EsClient struct {
	Client    *elastic.Client
	IndexName string
}

func (c EsClient) AddSensorDoc(doc SensorDoc) error {
	ctx := context.Background()
	if doc.Timestamp.IsZero() {
		doc.Timestamp = time.Now()
	}
	res, err := c.Client.Index().Index(c.IndexName).BodyJson(doc).Do(ctx)
	if err != nil {
		log.Errorf("failed to add sensor doc: %s %s", err, res)
	} else {
		log.Infof("Added sensor doc: %v", res)
	}
	return err
}

func NewElasticsearchClient(configs Configs) (*EsClient, error) {
	serverList := strings.Split(configs.ElasticServers, ",")
	client, err := elastic.NewClient(
		elastic.SetURL(serverList...),
		elastic.SetHealthcheck(false),
		elastic.SetSniff(false),
	)
	if err != nil {
		log.Fatalf("Failed to create elasticsearch Client: %s", err)
	}
	ec := &EsClient{
		Client:    client,
		IndexName: configs.IndexName,
	}
	return ec, err
}
