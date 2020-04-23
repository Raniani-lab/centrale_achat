# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    isReferenced = fields.Boolean("Referenced")
    reference_id = fields.Many2one('ref.res', "Reference number")
