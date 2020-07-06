# -*- coding: utf-8 -*-

from odoo import api, fields, models

SPLIT_METHOD = [
    ('equal', 'Equal'),
    ('by_quantity', 'by quantity'),
    ('by_current_cost_price', 'By cirrent price'),
    ('by_weight', 'By weight'),
    ('by_volume', 'By Volume'),
]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    landed_cost_ok = fields.Boolean(u'Import folder fees',default=False)
    split_method = fields.Selection(SPLIT_METHOD, u'Dispatch mode',default='by_current_cost_price')
    is_douane = fields.Boolean(u'Customs fees',default=False)
    is_copyright = fields.Boolean(u'Copyrights',default=False)
    taux_douane = fields.Float('Customs rates %',size='64',copy=False)
    copyright = fields.Float(u'Copyrights',size='64',copy=False)
