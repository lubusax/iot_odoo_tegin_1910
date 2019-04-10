from odoo import api, fields, models


class IotDeviceInput(models.Model):
    _inherit = 'iot.device.input'

    sensor_ids = fields.One2many('iot.sensor', inverse_name='input_id')

    @api.model
    def call_sensor(self, value):
        for sensor in self.sensor_ids:
            sensor.add_input(value)
        return {}
