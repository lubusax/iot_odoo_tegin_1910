from odoo import api, fields, models
import logging
logger = logging.getLogger(__name__)


class IotDeviceInput(models.Model):
    _inherit = 'iot.device.input'

    routing_key = fields.Char()

    @api.model
    def call_amqp(self, routing_key, delivery_tag, body):
        key = self.search([('routing_key', '=', routing_key)], limit=1)
        if key:
            key.call_device(body)
        else:
            logger.info('Key %s has not been found' % routing_key)
        return True

    @api.model
    def test_amqp_function(self, values):
        logger.info(values)
        return values
