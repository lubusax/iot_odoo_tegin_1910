from odoo import api, exceptions, fields, models, _
from odoo.tools.safe_eval import safe_eval
from jinja2.sandbox import SandboxedEnvironment
import json
import requests

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
    _description = 'IoT Template for Device'
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
    version_ids = fields.One2many(
        'iot.template.version',
        inverse_name='template_id',
    )
    current_version_id = fields.Many2one(
        'iot.template.version',
        readonly=True
    )

    def auto_generate_key(self, serial):
        self.ensure_one()
        return {'serial': serial}

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
    _description = 'IoT Input for Template'

    template_id = fields.Many2one('iot.template', required=True)
    name = fields.Char(required=True)
    params = fields.Text()
    call_model_id = fields.Many2one('ir.model')
    call_function = fields.Char(required=True)
    usage_link = fields.Char()
    usage_ids = fields.One2many(
        'iot.template.input.usage',
        inverse_name='template_input_id',
    )

    def _get_usage_information(self):
        # TODO: Define a place to store this information
        # The expected result should be a list with the following information:
        # [{'dependencies': ['addon_1', 'addon_2'...], 'name': 'NAME',
        # 'call_model': 'ir.model', 'call_function': 'function'},]
        response = requests.get(self.usage_link)
        response.raise_for_status()
        return json.loads(response.content.decode('utf-8'))

    def _check_usage_link(self):
        results = self._get_usage_information()
        new_vals = []
        existent = self.env['iot.template.input.usage']
        module_obj = self.env['ir.module.module']
        for result in results:
            dependancy_compatible = True
            for dependancy in result.get('dependencies', []):
                if not module_obj.search([
                    ('name', '=', dependancy),
                    ('state', '=', 'installed')
                ], limit=1):
                    dependancy_compatible = False
                    break
            if not dependancy_compatible:
                break
            model = self.env['ir.model'].search([
                ('name', '=', result['call_model'])
            ])
            usage = self.env['iot.template.input.usage'].search([
                ('template_input_id', '=', self.id),
                ('call_model_id', '=', model.id or False),
                ('call_function', '=', result['call_function'])
            ])
            if not usage:
                new_vals.append({
                    'name': result['name'],
                    'call_model_id': model.id or False,
                    'call_function': result['call_function']
                })
            existent |= usage
        (self.usage_ids - existent).unlink()
        self.write({'usage_ids': [(0,0, vals) for vals in new_vals]})

    @api.model
    def _check_usage_links(self):
        for record in self.search([('usage_link', '!=', False)]):
            record._check_usage_link()

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
    _description = 'Output templates for IoT'

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
    _description = 'IoT Keys for configuration'

    template_id = fields.Many2one('iot.template', required=True)
    key = fields.Char(required=True)


class IotTemplateInputUsage(models.Model):
    _name = 'iot.template.input.usage'
    _description = 'Usage of inputs'

    name = fields.Char()
    call_model_id = fields.Many2one('ir.model')
    call_function = fields.Char(required=True)
    template_input_id = fields.Many2one(
        'iot.template.input',
        required=True,
    )
    _sql_constraints = [(
        'usage_unique',
        'UNIQUE(call_model_id, call_function, template_input_id)',
        "Usage must be unique"
    )]


class IotTemplateVersion(models.Model):
    _name = 'iot.template.version'
    _description = 'IOT versions'

    template_id = fields.Many2one('iot.template', required=True)
    version = fields.Char()
    binary_file = fields.Binary(attachment=True)