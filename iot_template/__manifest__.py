# Copyright (C) 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'IoT Templates',
    'version': '11.0.1.0.0',
    'category': 'IoT',
    'author': "Creu Blanca, "
              "Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'installable': True,
    'summary': 'IoT base module',
    'depends': [
        'iot_input',
        'iot_input_sensor',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/iot_device_apply_template.xml',
        'views/iot_device_views.xml',
    ],
}
