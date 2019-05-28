# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IotDeviceInputUsageWizard(models.TransientModel):
    _name = 'iot.device.input.usage.wizard'

    input_id = fields.Many2one(
        'iot.device.input',
        required=True
    )
    template_input_id = fields.Many2one(
        'iot.template.input',
        required=True
    )
    usage_id = fields.Many2one(
        'iot.template.input.usage',
        required=True
    )

    @api.multi
    def doit(self):
        return
