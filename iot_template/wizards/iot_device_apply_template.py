from odoo import api, fields, models


class IotDeviceApplyTemplate(models.TransientModel):
    _name = 'iot.device.apply.template'

    device_id = fields.Many2one('iot.device', readonly=True, required=True)
    template_id = fields.Many2one('iot.template', required=True)
    value_ids = fields.One2many(
        'iot.device.apply.template.values',
        inverse_name='apply_template_id'
    )

    @api.onchange('template_id')
    def _onchange_values(self):
        self.value_ids = self.env['iot.device.apply.template.values']
        for key in self.template_id.get_keys():
            self.value_ids |= self.value_ids.create({
                'key': key
            })

    @api.multi
    def run(self):
        self.ensure_one()
        self.template_id.apply_template(self.device_id, {
            r.key: r.value for r in self.value_ids
        })


class IotDeviceApplyTemplateValues(models.TransientModel):
    _name = 'iot.device.apply.template.values'

    apply_template_id = fields.Many2one('iot.device.apply.template')
    key = fields.Char(required=True, readonly=True)
    value = fields.Char()
