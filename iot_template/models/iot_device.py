from odoo import api, models


class IotDevice(models.Model):
    _inherit = 'iot.device'

    @api.multi
    def get_iot_configuration(self):
        self.ensure_one()
        return {
            'name': self.name,
            'outputs': {
                output.name: output.get_configuration()
                for output in self.output_ids
            },
            'inputs': {
                iot_input.name: iot_input.get_configuration()
                for iot_input in self.input_ids
            }
        }
