from odoo import models
import os
import logging
_logger = logging.getLogger(__name__)
try:
    import paho.mqtt.client as mqtt
except (ImportError, IOError) as err:
    _logger.debug(err)


class IoTSystemAction(models.Model):
    _inherit = 'iot.system.action'

    def _run(self, device_action):
        if self != self.env.ref('iot_mqtt.mqtt_action'):
            return super()._run(device_action)
        url = self.env['ir.config_parameter'].sudo().get_param(
            'mqtt.host'
        )
        port = int(self.env['ir.config_parameter'].sudo().get_param(
            'mqtt.port', "1883"
        ))
        client = mqtt.Client()
        client.connect(url, port)
        client.username_pw_set("odoo", "odoo    ")
        import logging
        logging.info(
            client.publish(
                device_action.output_id.mqtt_topic,
                device_action.output_id.mqtt_payload
            ))
        client.disconnect()
