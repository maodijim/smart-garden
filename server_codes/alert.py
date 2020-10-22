import smtplib
import logging
import sys
import time
import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


class AlertConf:
    ALERT_THRESHOLD = "alert_threshold"
    ALERT_DEVICE_IDS = "alert_device_ids"
    ALERT_FIELDS = "alert_fields"
    ALERT_GRACE_SECS = "alert_grace_period_secs"


class AlertAction:
    def __init__(self, smtp_server, smtp_user, smtp_pass, alert_settings, email_settings, smtp_port=587, ssl=True):
        self.alert_settings = alert_settings
        self.email_settings = email_settings
        self.smtp_user = smtp_user
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.__smtp_pass = smtp_pass
        self.ssl = ssl
        self.server = None
        self.threshold = int(alert_settings.get(AlertConf.ALERT_THRESHOLD, 0))
        self.device_ids = alert_settings.get(AlertConf.ALERT_DEVICE_IDS, "").split(",")
        self.alert_fields = alert_settings.get(AlertConf.ALERT_FIELDS, "").split(",")
        self.alert_grace_secs = int(alert_settings.get(AlertConf.ALERT_GRACE_SECS, 100))
        self.last_alert = {}
        self.subject = "Notice: Device Id {}, Device Name {} alert trigger"
        self.body = """ At {alert_time} {device_name}: {field} reach {val} above threshold {threshold} """

    def smtp_connect(self):
        try:
            self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.ssl:
                self.server.starttls()
            self.server.login(self.smtp_user, self.__smtp_pass)
        except Exception as e:
            logging.error(e)

    def check_alert(self, device_id, device_name, metrics):
        """

        :param device_id:
        :param device_name:
        :param metrics: dict
        """
        if metrics is dict():
            logging.warning("Metrics is not dict")
            return
        logging.info("checking alert for device id {} device name {}".format(device_id, device_name))
        if device_id not in self.device_ids:
            logging.info("Device Id {} not set for alert".format(device_id))
            return
        logging.info("Device ID {} is set for alert, checking fields".format(device_id))
        for field in self.alert_fields:
            logging.info("checking alert field: {}".format(field))
            if metrics.get(field, None):
                if int(metrics.get(field)) > self.threshold and time.time() - self.alert_grace_secs >= self.last_alert.get(device_id, time.time() - self.alert_grace_secs):
                    logging.info("alert field {} meet threshold {}".format(field, self.threshold))
                    self.smtp_connect()
                    self.send_email(
                        self.smtp_user,
                        self.email_settings['send_to'],
                        self.subject.format(device_id, device_name),
                        self.body.format(
                            alert_time=datetime.datetime.now(),
                            device_name=device_name,
                            field=field,
                            val=metrics.get(field),
                            threshold=self.threshold
                        )
                    )
                    self.server.quit()
                elif time.time() - self.alert_grace_secs <= self.last_alert.get(device_id, time.time()):
                    logging.info("Alert Grace Period not meet for device {}".format(device_id))
            else:
                logging.info("Field {} not found in metrics: {}".format(field, metrics))
                return
            self.last_alert[device_id] = time.time()

    def send_email(self, send_from, send_to, subject, body):
        email_text = """\
Subject: {}

{}""".format(
            subject,
            body
        )
        try:
            logging.info("Sending alert email to {}".format(send_to))
            self.server.sendmail(send_from, send_to, email_text)
        except Exception as e:
            logging.error("Failed to send email: {}".format(e))
