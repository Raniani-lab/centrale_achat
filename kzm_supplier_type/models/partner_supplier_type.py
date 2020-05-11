# -*- coding: utf-8 -*-

from odoo import models, fields, _


class SuppType(models.Model):
    _name = 'partner.supplier.type'
    _description = "Supplier Types"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)

    _sql_constraints = [

        ('name_unique',
         'UNIQUE(code)',
         "The code must be unique"),
    ]


class ResPartnerSupp(models.Model):
    _inherit = "res.partner"

    supplier_type_id = fields.Many2one('partner.supplier.type', string="Supplier Nature")
