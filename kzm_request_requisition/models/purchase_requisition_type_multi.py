
from odoo import tools
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


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    partner_id = fields.Many2one('res.partner', related="order_id.partner_id")
    requisition_id = fields.Many2one('purchase.requisition', related="order_id.requisition_id")
    date_end = fields.Datetime(related="order_id.requisition_id.date_end")


# class MultipleConsultationReport(models.Model):
#     _name = 'purchase.order.pivot'
#     _description = "Purchase order pivot"
#
#     product_id = fields.Many2one('product.template', string='Product', readonly=True)
#     purchase_order_id = fields.Many2one('purchase.order', string="Purchase order", readonly=True)
#     order_line = fields.One2many('purchase.order.line', string="Order Line", readonly=True)
#     partner_id = fields.Many2one('res.partner', string="Supplier", readonly=True)
#     price_subtotal = fields.Monetary(string="Price subtotal", readonly=True)
#
#     def init(self):
#         tools.drop_view_if_exists(self.env.cr, 'purchase_order_report_analysis')
#         self.env.cr.execute("""
#             CREATE VIEW purchase_order_report_analysis AS (
#                 SELECT
#                     O.id as id,
#                     L.product_id AS product_id,
#                     L.purchase_order_id AS purchase_order_id,
#                     O.partner_id AS partner_id,
#                     L.price_subtotal AS price_subtotal,
#                 FROM purchase_order T
#                     LEFT JOIN purchase_order_line L ON (O.id = L.purchase_order_id)
#                 )
#             """)