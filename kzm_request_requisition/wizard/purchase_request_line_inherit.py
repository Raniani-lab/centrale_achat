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
                                  default='purchase_contract', string='Convert To')
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        required=False,
        domain=[("supplier_rank", ">", 0)],
        context={"supplier_rank": 1},
    )
    purchase_contract_id = fields.Many2one('purchase.requisition', string="Purchase contract",
                                           domain="[('state','=','ongoing')]")
    supplier_ids = fields.Many2many('res.partner', string="Suppliers", domain="[('supplier_rank','=',True)]")

    def _get_products_from_contract(self, contract):
        products = []
        for line in contract.line_ids:
            products.append(line.product_id)
        return products

    def _get_product_qty_from_contract(self,contract, product):
        qty=0
        for line in contract.line_ids:
            if line.product_id.id == product.id:
                qty = line.product_qty
        return qty

    @api.onchange('purchase_contract_id')
    def _compute_quantity_max(self):
        self.ensure_one()
        if self.purchase_contract_id:
            products = self._get_products_from_contract(self.purchase_contract_id)
            for item in self.item_ids:
                if item.product_id in products:
                    item.quantity_max = self._get_product_qty_from_contract(self.purchase_contract_id, item.product_id)
                if item.product_id in products and self.get_total_quantity(item.product_id) <= self.get_quantity_from_contract(self.purchase_contract_id, item.product_id):
                    item.status = 'eligible'
                else:
                    item.status = 'non_eligible'

    @api.onchange('supplier_id')
    def onchange_supplier_contract(self):
        for o in self:
            res={}
            o.purchase_contract_id = False
            if o.supplier_id:
                res = {'domain': {
                    'purchase_contract_id': [('vendor_id', '=', o.supplier_id.id),
                                             ('state', '=', 'ongoing'),
                                             ('type_id', '=', self.env.ref("purchase_requisition.type_single").id)]}}
        return res

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

    def get_quantity_from_contract(self, contract, product):
        qty=0
        for line in contract.line_ids:
            if line.product_id.id == product.id:
                qty = qty + line.product_qty
        return qty

    def get_total_quantity(self, product):
        qty=0
        for o in self:
            for item in o.item_ids:
                if item.product_id.id == product.id:
                    qty = qty + item.product_qty
        return qty

    def generate_base_on_contract(self):
        self.ensure_one()
        res = []
        purchase_obj = self.env["purchase.order"]
        po_line_obj = self.env["purchase.order.line"]
        pr_line_obj = self.env["purchase.request.line"]
        purchase = False
        for item in self.item_ids:
            line = item.line_id
            if item.product_qty <= 0.0:
                raise UserError(_("Enter a positive quantity."))
            if item.status == 'non_eligible':
                raise UserError(_("The product '%s' does not exist or exceed the quantity in the contract.") % item.product_id.name)
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
            po_line.name = item.name
            po_line.product_qty = self.get_total_quantity(item.product_id)
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
            if o.supplier_ids.ids == []:
                raise UserError(_("Please insert at least One supplier."))
            else:
                new_convention = self.env['purchase.requisition'].create({
                    'type_id': self.env.ref('purchase_requisition.type_multi').id,
                    'multiple_consultation': True,
                    'supplier_ids': o.supplier_ids,
                })
                for item in o.item_ids:
                    new_convention.line_ids = [(0, 0, {
                                                    'product_id': item.product_id.id,
                                                    'product_qty': item.product_qty,
                                                    'display_name': item.name,
                                                    })]
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


class PurchaseRequestLineMakePurchaseOrderItem(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order.item'

    quantity_max = fields.Integer(string="Quantity maximum")
    status = fields.Selection([('eligible', 'Eligible'), ('non_eligible', 'Non Eligible')],
                              string="Status")





