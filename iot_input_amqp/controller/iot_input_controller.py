# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from odoo import http


class CallIot(http.Controller):
    @http.route([
        '/iot/<routing_key>/action_amqp',
        ], type='http', auth="none", methods=['POST'], csrf=False)
    def call_unauthorized_iot(self, routing_key, *args, **kwargs):
        request = http.request
        if not request.env:
            return json.dumps({})
        return json.dumps(request.env['iot.device.input'].sudo().call_amqp(
            routing_key,
            kwargs['delivery_tag'],
            kwargs['body']
        ) or {})
