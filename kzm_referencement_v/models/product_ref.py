# -*- coding: utf-8 -*-
from odoo.addons import decimal_precision as dp
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, RedirectWarning, UserError


class ProductRef(models.Model):
    """ Represente  """

    _name = 'ref.product'
    _description = "Referencement of product"
    _inherit = ['ref.ref', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char("Ref sequence", default='New')
    prod_name = fields.Char("Product Name")
    sale_ok = fields.Boolean('Can be Sold', default=True)
    purchase_ok = fields.Boolean('Can be Purchased', default=True)
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Stockable Product')], string='Product Type', default='consu', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')

    def _get_default_category_id(self):
        if self._context.get('categ_id') or self._context.get('default_categ_id'):
            return self._context.get('categ_id') or self._context.get('default_categ_id')
        category = self.env.ref('product.product_category_all', raise_if_not_found=False)
        if not category:
            category = self.env['product.category'].search([], limit=1)
        if category:
            return category.id
        else:
            err_msg = _('You must define at least one product category in order to be able to create products.')
            redir_msg = _('Go to Internal Categories')
            raise RedirectWarning(err_msg, self.env.ref('product.product_category_action_form').id, redir_msg)

    default_code = fields.Char(
        'Internal Reference', store=True)
    categ_id = fields.Many2one('product.category', 'Product Category', change_default=True, required=True,
                               help="Select category for the current product", default=_get_default_category_id)
    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits=dp.get_precision('Product Price'),
        help="Price at which the product is sold to customers.")

    standard_price = fields.Float(
        'Cost', digits=dp.get_precision('Product Price'), groups="base.group_user",
        help="Cost used for stock valuation in standard price and as a first price to set in average/FIFO.")
# seller_ids = fields.One2many('product.supplierinfo', 'product_tmpl_id', 'Vendors', help="Define vendor pricelists.")
    description_purchase = fields.Text(
        'Purchase Description', translate=True)
    description_sale = fields.Text(
        'Sale Description', translate=True,
        help="A description of the Product that you want to communicate to your customers. "
             "This description will be copied to every Sales Order, Delivery Order and Customer Invoice/Credit Note")
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Sent"),
        ('done', "Approved"),
        ('refused', "Refused"),
    ], default='draft', track_visibility='onchange')

    currency_id = fields.Many2one(
        'res.currency', 'Currency', compute='_compute_currency_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)

    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id

    def action_draft(self):
        self.state = 'draft'

    def action_confirm(self):
        self.state = 'confirmed'

    def action_refuse(self):
        self.state = 'refused'

    def action_done(self):
        self.env['product.template'].create({
            'name': self.prod_name,
            'sale_ok': self.sale_ok,
            'purchase_ok': self.purchase_ok,
            'type': self.type,
            'default_code': self.default_code,
            'categ_id': self.categ_id.id,
            'list_price': self.list_price,
            'standard_price': self.standard_price,
            'description_purchase': self.description_purchase,
            'description_sale': self.description_sale,
            'isReferenced': True,
            'reference_id': self.id,
        })
        self.state = 'done'

    @api.onchange('prod_name')
    def _verify_valid_name(self):
        name = self.env['product.template'].search([
            ('name', '=', self.prod_name)
        ])
        if name:
            return {
                'warning': {
                    'title': _("Product name"),
                    'message': _("Product name already exits"),
                },
            }

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('ref.product') or 'REF'
        vals['name'] = seq
        return super(ProductRef, self).create(vals)

    def product_ref(self):
        """action de redirection le produit reference """
        evals_recaps = self.env['product.template'].search([('name', '=', self.prod_name)])
        action = self.env.ref('purchase.product_normal_action_puchased').read()[0]
        if len(evals_recaps) > 1:
            action['domain'] = [('id', 'in', evals_recaps.ids)]
        elif len(evals_recaps) == 1:
            action['views'] = [(self.env.ref('product.product_template_form_view').id, 'form')]
            action['res_id'] = evals_recaps.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(prod_name)',
         "The name  must be unique"),
    ]