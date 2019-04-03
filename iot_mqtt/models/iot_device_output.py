from odoo import fields, models


class IotDeviceOutput(models.Model):
    _inherit = 'iot.device.output'

    mqtt_topic = fields.Char()
    mqtt_payload = fields.Char()
