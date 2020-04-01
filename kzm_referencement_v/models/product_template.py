# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class ProductTemplate(models.Model):
    """ Represente  """

    _inherit = 'product.template'
    _description = "Referencement of product"

    isReferenced = fields.Boolean("Referenced")
    reference_id = fields.Many2one('ref.product', "Reference number")
    # @api.multi
    # def _get_reference(self):
    #     for r in self:
    #         r.reference_id = r.env['product.template'].search([('name', '=', r.name)]).id
    #         r.isReferenced = True if r.reference_id else False
    #compute = '_get_reference'

    def product_ref(self):
        pass

