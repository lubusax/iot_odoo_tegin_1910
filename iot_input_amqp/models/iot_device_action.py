from odoo import models
import os
from odoo.tools import config
import logging
_logger = logging.getLogger(__name__)
try:
    import pika
except (ImportError, IOError) as err:
    _logger.debug(err)


class IoTSystemAction(models.Model):
    _inherit = 'iot.system.action'

    def _run(self, device_action):
        if self != self.env.ref('iot_input_amqp.amqp_action'):
            return super()._run(device_action)
        url = (os.environ.get('ODOO_AMQP_BROKER') or
               config.misc.get("amqp", {}).get('broker') or
               config['amqp_broker'])
        connection = pika.BlockingConnection(pika.URLParameters(url))
        channel = connection.channel()
        channel.publish(
            device_action.output_id.exchange,
            routing_key=device_action.output_id.routing_key,
            body=device_action.output_id.body
        )
