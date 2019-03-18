from odoo import api, models, _


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        if self.env.context.get('iot_device_name', False):
            body = vals.get('body', '')
            if len(body) > 0:
                body += '<br>'
            vals['body'] = '%s%s' % (
                body, _(
                    'Detected automatically by %s'
                ) % self.env.context.get('iot_device_name')
            )
        return super().create(vals)
