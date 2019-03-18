from odoo import fields, models


class IotDeviceOutput(models.Model):
    _inherit = 'iot.device.output'

    routing_key = fields.Char()
    exchange = fields.Char()
    body = fields.Char()
