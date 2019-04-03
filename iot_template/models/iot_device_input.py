from odoo import api, models


class IotDeviceInput(models.Model):
    _inherit = 'iot.device.input'

    @api.multi
    def get_configuration(self):
        return {
            'serial': self.serial,
            'passphrase': self.passphrase,
        }
