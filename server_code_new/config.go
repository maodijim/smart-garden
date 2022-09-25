package main

import (
	"github.com/BurntSushi/toml"
	log "github.com/sirupsen/logrus"
)

type (
	Alert struct {
		AlertDeviceId    string `toml:"alert_device_id"`
		AlertAction      string `toml:"alert_action"`
		AlertFields      string `toml:"alert_fields"`
		AlertThreshold   int    `toml:"alert_threshold"`
		AlertGracePeriod string `toml:"alert_grace_period"`
	}

	Email struct {
		SmtpServer string `toml:"smtp_server"`
		SmtpPort   int    `toml:"smtp_port"`
		SmtpUser   string `toml:"email_username"`
		SmtpPass   string `toml:"email_password"`
		SendTo     string `toml:"send_to"`
	}

	MqttServerConf struct {
		MqttServer string `toml:"mqtt_server"`
		MqttPort   int    `toml:"mqtt_port"`
		MqttUser   string `toml:"mqtt_user"`
		MqttPass   string `toml:"mqtt_pass"`
	}

	Configs struct {
		LogLevel       string                    `toml:"log_level"`
		MqttServers    map[string]MqttServerConf `toml:"mqtt_server"`
		ElasticServers string                    `toml:"elastic_servers"`
		ElasticPort    int                       `toml:"elastic_server_port"`
		IndexName      string                    `toml:"index_name"`
		Alert          `toml:"alert"`
		Email          `toml:"email"`
	}
)

func loadConfigs(path string) *Configs {
	// load toml configs from path
	conf := &Configs{}
	_, err := toml.DecodeFile(path, conf)
	if err != nil {
		log.Fatalf("Failed to load configs from path %s: %s", path, err)
	}
	return conf
}
