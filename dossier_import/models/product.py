# -*- coding: utf-8 -*-

from odoo import api, fields, models

SPLIT_METHOD = [
    ('equal', 'Egal'),
    ('by_quantity', 'Par Quantité'),
    ('by_current_cost_price', 'Par prix actuel'),
    ('by_weight', 'Par Poids'),
    ('by_volume', 'Par Volume'),
]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    landed_cost_ok = fields.Boolean(u'Frais dossier import',default=False)
    split_method = fields.Selection(SPLIT_METHOD, u'Mode répartition',default='by_current_cost_price')
    is_douane = fields.Boolean(u'Frais douane',default=False)
    is_copyright = fields.Boolean(u'Droits d\'auteurs',default=False)
    taux_douane = fields.Float('Taux douane %',size='64',copy=False)
    copyright = fields.Float(u'Droits d\'auteurs',size='64',copy=False)
