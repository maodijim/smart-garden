package main

import (
	log "github.com/sirupsen/logrus"
)

var (
	esClient = &EsClient{}
)

func init() {
	log.SetFormatter(&log.TextFormatter{
		DisableColors: false,
		FullTimestamp: true,
		ForceColors:   true,
	})
	log.SetLevel(log.InfoLevel)
}

func main() {
	conf := loadConfigs("configs.conf")
	esClient, _ = NewElasticsearchClient(*conf)
	_, _ = NewMqttClients(*conf)

	<-make(chan struct{})
}
