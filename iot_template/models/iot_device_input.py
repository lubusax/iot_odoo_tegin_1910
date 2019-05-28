from odoo import api, fields, models


class IotDeviceInput(models.Model):
    _inherit = 'iot.device.input'

    template_input_id = fields.Many2one(
        'iot.template.input',
        readonly=True,
    )
    usage_ids = fields.One2many(
        'iot.template.input.usage',
        related='template_input_id.usage_ids',
        readonly=True,
    )

    @api.multi
    def get_configuration(self):
        return {
            'serial': self.serial,
            'passphrase': self.passphrase,
        }
