# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    expense_medical_product_id = fields.Many2one(related='company_id.expense_medical_product_id', string="Expense medical product",
                                     readonly=False)




class Company(models.Model):
    _inherit = 'res.company'

    expense_medical_product_id = fields.Many2one('product.product', string="Expense medical product")

