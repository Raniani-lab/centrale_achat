
from datetime import datetime

from odoo import _, api, fields, models, exceptions
from odoo.exceptions import UserError


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    supplier_ids = fields.Many2many('res.partner', string="Suppliers", domain="[('supplier_rank','=',True)]")
    multiple_consultation = fields.Boolean()

    @api.onchange('type_id')
    def onchange_type_set_multiple(self):
        for o in self:
            if o.type_id:
                if o.type_id.id == self.env.ref("purchase_requisition.type_multi").id:
                    o.multiple_consultation = True
                else:
                    o.multiple_consultation = False

    def generate_quotation_requests(self):
        for o in self:
            if o.supplier_ids.ids != []:
                for supplier in o.supplier_ids:
                    new_order = self.env['purchase.order'].create({
                        'partner_id': supplier.id,
                        'requisition_id': o.id,
                        'state': 'draft',
                    })
                    for item in o.line_ids:
                        new_order.order_line = [(0, 0, {
                            'order_id': new_order and new_order.id,
                            'product_id': item.product_id.id,
                            'name': item.display_name,
                            'product_qty': item.product_qty,
                            'price_unit': item.price_unit,
                            'date_planned': fields.Date.today(),
                            "product_uom": item.product_id.uom_id.id,
                        })]
            else:
                exceptions.ValidationError(_("Please make sure you have at least One supplier"))