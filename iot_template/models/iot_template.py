from odoo import api, exceptions, fields, models, _
from odoo.tools.safe_eval import safe_eval
from jinja2.sandbox import SandboxedEnvironment

mako_template_env = SandboxedEnvironment(
    block_start_string="<%",
    block_end_string="%>",
    variable_start_string="${",
    variable_end_string="}",
    comment_start_string="<%doc>",
    comment_end_string="</%doc>",
    line_statement_prefix="%",
    line_comment_prefix="##",
    trim_blocks=True,               # do not output newline after blocks
    autoescape=True,                # XML/HTML automatic escaping
)


class IotTemplate(models.Model):
    _name = 'iot.template'
    _parent_name = 'parent_id'
    _parent_store = True
    _parent_order = 'name'

    parent_left = fields.Integer(index=True)
    parent_right = fields.Integer(index=True)
    name = fields.Char(required=True)
    input_ids = fields.One2many(
        'iot.template.input', inverse_name='template_id',
    )
    output_ids = fields.One2many(
        'iot.template.output', inverse_name='template_id',
    )
    key_ids = fields.One2many('iot.template.key', inverse_name='template_id')
    parent_id = fields.Many2one('iot.template', ondelete='restrict')

    @api.multi
    def get_keys(self):
        keys = [key.key for key in self.key_ids]
        if self.parent_id:
            keys += self.parent_id.get_keys()
        return keys

    @api.multi
    @api.constrains('parent_id')
    def _check_recursion_parent_id(self):
        if not self._check_recursion():
            raise exceptions.ValidationError(
                _('Error! You are attempting to create a recursive template.'))

    @api.multi
    def apply_template(self, device, keys):
        self.ensure_one()
        for element in self.input_ids:
            element._apply_template(device, keys)
        for element in self.output_ids:
            element._apply_template(device, keys)
        if self.parent_id:
            self.parent_id.apply_template(device, keys)


class IotTemplateInput(models.Model):
    _name = 'iot.template.input'

    template_id = fields.Many2one('iot.template', required=True)
    name = fields.Char(required=True)
    params = fields.Text()
    call_model_id = fields.Many2one('ir.model')
    call_function = fields.Char(required=True)

    def _apply_template(self, device, keys):
        real_vals = {
            'device_id': device.id,
            'name': self.name,
            'call_function': self.call_function,
            'call_model_id': self.call_model_id.id,
        }
        vals = safe_eval(self.params)
        for key in vals:
            vals[key] = mako_template_env.from_string(vals[key]).render(keys)
        real_vals.update(vals)
        return self.env['iot.device.input'].create(real_vals)


class IotTemplateOutput(models.Model):
    _name = 'iot.template.output'

    template_id = fields.Many2one('iot.template', required=True)
    name = fields.Char(required=True)
    system_id = fields.Many2one('iot.system', required=True)
    params = fields.Text()

    def _apply_template(self, device, keys):
        real_vals = {
            'device_id': device.id,
            'name': self.name,
            'system_id': self.system_id.id
        }
        vals = safe_eval(self.params)
        for key in vals:
            vals[key] = mako_template_env.from_string(vals[key]).render(keys)
        real_vals.update(vals)
        return self.env['iot.device.output'].create(real_vals)


class IotTemplateKey(models.Model):
    _name = 'iot.template.key'

    template_id = fields.Many2one('iot.template', required=True)
    key = fields.Char(required=True)
