# Copyright (C) 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'IoT Sensor',
    'version': '11.0.1.0.0',
    'category': 'IoT',
    'author': "Creu Blanca, "
              "Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'installable': True,
    'summary': 'IoT base module',
    'depends': [
        'iot_input',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/iot_sensor_views.xml',
    ],
}
