# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    set_sale_visible = fields.Boolean()
    set_purchase_visible = fields.Boolean()

    @api.model
    def default_get(self, default_fields):
        res = super(ProductTemplate, self).default_get(default_fields)
        sale_model = self.env['ir.module.module'].search([('name', '=', 'sale')])
        if sale_model and sale_model.state == "installed":
            res['sale_ok'] = True
            res['set_sale_visible'] = True
        else:
            res['sale_ok'] = False
            res['set_sale_visible'] = False
        purchase_model = self.env['ir.module.module'].search([('name', '=', 'purchase')])
        if purchase_model and purchase_model.state == "installed":
            res['purchase_ok'] = True
            res['set_purchase_visible'] = True
        else:
            res['purchase_ok'] = False
            res['set_purchase_visible'] = False
        return res
