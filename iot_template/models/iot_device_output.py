from odoo import api, models


class IotDeviceOutput(models.Model):
    _inherit = 'iot.device.output'

    @api.multi
    def get_configuration(self):
        return {

        }
