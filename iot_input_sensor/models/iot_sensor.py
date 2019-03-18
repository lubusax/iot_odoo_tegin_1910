from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import json


class IotSensor(models.Model):
    _name = 'iot.sensor'

    name = fields.Char(required=True)
    input_id = fields.Many2one('iot.device.input')
    query = fields.Char()
    restart_type = fields.Selection([
        ('daily', 'Daily'),
        ('monthly', 'Monthly')
    ])
    value_ids = fields.One2many(
        'iot.sensor.value', inverse_name='sensor_id'
    )

    @api.model
    def _compute_date(self, restart, original_date):
        date = original_date
        if restart in ['daily', 'monthly']:
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        if restart == 'monthly':
            date = date.replace(day=1)
        return date

    def get_date(self, values):
        return fields.Datetime.from_string(fields.Datetime.now())

    def add_input(self, values):
        self.ensure_one()
        date = self.get_date(values)
        new_date = fields.Datetime.to_string(
            self._compute_date(self.restart_type, date))
        val = values
        if self.query:
            if isinstance(val, str):
                val = json.loads(val)
            for query in self.query.split('/'):
                val = val[query]
        if not isinstance(val, (int, float, str)):
            raise ValidationError(_('Value %s must be a float') % val)
        val = float(val)
        value = self.env['iot.sensor.value'].search([
            ('sensor_id', '=', self.id),
            ('date', '=', new_date)
        ])
        if not value:
            value.create({
                'sensor_id': self.id,
                'date': new_date,
                'value': val,
                'min_value': val,
                'max_value': val,
            })
        else:
            vals = {'value': val}
            if value.min_value > val:
                vals['min_value'] = val
            if value.max_value < val:
                vals['max_value'] = val
            value.write(vals)


class IotSensorValues(models.Model):
    _name = 'iot.sensor.value'

    sensor_id = fields.Many2one('iot.sensor', required=True, readonly=True)
    date = fields.Datetime(required=True, readonly=True)
    min_value = fields.Float(required=True, readonly=True)
    max_value = fields.Float(required=True, readonly=True)
    value = fields.Float(required=True, readonly=True)
