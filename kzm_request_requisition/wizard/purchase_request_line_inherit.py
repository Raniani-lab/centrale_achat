from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class PurchaseRequestLineGenerationType(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'
    _description = 'add convert to field'

    convert_to = fields.Selection([('purchase_contract', 'Purchase contract'),
                                   ('multiple_consultation', 'Multiple consultation'),
                                   ('request_quotation', 'Request for Quotation')],
                                  string='Convert To')
    supplier_id = fields.Many2one('res.partner', string="Supplier", domain="[('supplier_rank','=',True)]")
    purchase_contract_id = fields.Many2one('purchase.requisition', string="Purchase contract",
                                           domain="[('state','=','ongoing')]")
    supplier_wizard_ids = fields.One2many('purchase.request.line.supplier', 'purchase_request_line_id', string="Suppliers")
    supplier_ids = fields.Many2many('res.partner', string="Suppliers", )

    @api.onchange('supplier_id')
    def onchange_supplier_contract(self):
        for o in self:
            o.purchase_contract_id = False
            if o.supplier_id:
                res = {'domain': {
                    'purchase_contract_id': [('vendor_id', '=', o.supplier_id or o.supplier_id.id)]}}

    @api.model
    def _prepare_purchase_order(self, picking_type, group_id, company, origin):
        if not self.supplier_id:
            raise UserError(_("Enter a supplier."))
        supplier = self.supplier_id
        data = {
            "origin": origin,
            "partner_id": self.supplier_id.id,
            "requisition_id": self.purchase_contract_id.id,
            "fiscal_position_id": supplier.property_account_position_id
                                  and supplier.property_account_position_id.id
                                  or False,
            "picking_type_id": picking_type.id,
            "company_id": company.id,
            "group_id": group_id.id,
        }
        return data

    def generate_base_on_contract(self):
        res = []
        purchase_obj = self.env["purchase.order"]
        po_line_obj = self.env["purchase.order.line"]
        pr_line_obj = self.env["purchase.request.line"]
        purchase = False

        for item in self.item_ids:
            line = item.line_id
            if item.product_qty <= 0.0:
                raise UserError(_("Enter a positive quantity."))
            if self.purchase_order_id:
                purchase = self.purchase_order_id
            if not purchase:
                po_data = self._prepare_purchase_order(
                    line.request_id.picking_type_id,
                    line.request_id.group_id,
                    line.company_id,
                    line.origin,
                )
                purchase = purchase_obj.create(po_data)

            # Look for any other PO line in the selected PO with same
            # product and UoM to sum quantities instead of creating a new
            # po line
            domain = self._get_order_line_search_domain(purchase, item)
            available_po_lines = po_line_obj.search(domain)
            new_pr_line = True
            # If Unit of Measure is not set, update from wizard.
            if not line.product_uom_id:
                line.product_uom_id = item.product_uom_id
            # Allocation UoM has to be the same as PR line UoM
            alloc_uom = line.product_uom_id
            wizard_uom = item.product_uom_id
            if available_po_lines and not item.keep_description:
                new_pr_line = False
                po_line = available_po_lines[0]
                po_line.purchase_request_lines = [(4, line.id)]
                po_line.move_dest_ids |= line.move_dest_ids
                po_line_product_uom_qty = po_line.product_uom._compute_quantity(
                    po_line.product_uom_qty, alloc_uom
                )
                wizard_product_uom_qty = wizard_uom._compute_quantity(
                    item.product_qty, alloc_uom
                )
                all_qty = min(po_line_product_uom_qty, wizard_product_uom_qty)
                self.create_allocation(po_line, line, all_qty, alloc_uom)
            else:
                po_line_data = self._prepare_purchase_order_line(purchase, item)
                if item.keep_description:
                    po_line_data["name"] = item.name
                po_line = po_line_obj.create(po_line_data)
                po_line_product_uom_qty = po_line.product_uom._compute_quantity(
                    po_line.product_uom_qty, alloc_uom
                )
                wizard_product_uom_qty = wizard_uom._compute_quantity(
                    item.product_qty, alloc_uom
                )
                all_qty = min(po_line_product_uom_qty, wizard_product_uom_qty)
                self.create_allocation(po_line, line, all_qty, alloc_uom)
            # TODO: Check propagate_uom compatibility:
            new_qty = pr_line_obj._calc_new_qty(
                line, po_line=po_line, new_pr_line=new_pr_line
            )
            po_line.product_qty = new_qty
            po_line._onchange_quantity()
            # The onchange quantity is altering the scheduled date of the PO
            # lines. We do not want that:
            date_required = item.line_id.date_required
            po_line.date_planned = datetime(
                date_required.year, date_required.month, date_required.day
            )
            res.append(purchase.id)

        return {
            "domain": [("id", "in", res)],
            "name": _("RFQ"),
            "view_mode": "tree,form",
            "res_model": "purchase.order",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }

    def generate_base_on_consultation(self):
        self.ensure_one()
        lines = self.env['ir.model.data'].sudo().search([
                    ('id', 'in', self.item_ids.ids)
                ])
        for o in self:
            vals = []
            for item in o.item_ids:
                print(item.product_qty)
                vals.append({
                    'product_id': item.product_id and item.product_id.id,
                    'product_qty': 6,
            })
            new_convention = self.env['purchase.requisition'].create({
                'type_id': self.env.ref('purchase_requisition.type_multi').id,
            })
        return {
            # 'name': self.order_id,
            'res_model': 'purchase.requisition',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new_convention.id,
            'view_id': self.env.ref("purchase_requisition.view_purchase_requisition_form").id,
            'target': 'target'
        }


class PurchaseRequestLineSupplier(models.TransientModel):
    _name = 'purchase.request.line.supplier'
    _description = 'Purchase Request Line Supplier'

    supplier_id = fields.Many2one('res.partner', string="Supplier", domain="[('supplier_rank','=',True)]")
    purchase_request_line_id = fields.Many2one('purchase.request.line.make.purchase.order')




