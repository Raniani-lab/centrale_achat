# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from odoo import models, api, fields
import odoo.addons.decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_costed = fields.Boolean(default=False)

    def action_open_landed_cost(self):
        self.ensure_one()
        line_obj = self.env['purchase.cost.distribution.line']
        lines = line_obj.search([('picking_id', '=', self.id)])
        if lines:
            mod_obj = self.env['ir.model.data']
            model, action_id = tuple(
                mod_obj.get_object_reference(
                    'purchase_landed_cost',
                    'action_purchase_cost_distribution'))
            action = self.env[model].browse(action_id).read()[0]
            ids = set([x.distribution.id for x in lines])
            if len(ids) == 1:
                res = mod_obj.get_object_reference(
                    'purchase_landed_cost', 'purchase_cost_distribution_form')
                action['views'] = [(res and res[1] or False, 'form')]
                action['res_id'] = list(ids)[0]
            else:
                action['domain'] = "[('id', 'in', %s)]" % list(ids)
            return action


class StockMove(models.Model):
    _inherit = 'stock.move'

    old_price_unit = fields.Float('Old Unit Price', digits=dp.get_precision('Product Price'))

    def product_price_update_after_done(self):
        ''' Adapt standard price on outgoing moves, so that a
        return or an inventory loss is made using the last value used for an outgoing valuation. '''
        # to_update_moves = self.filtered(lambda move: move.location_dest_id.usage != 'internal')
        # to_update_moves._store_average_cost_price()
        self._store_average_cost_price()

    def _store_average_cost_price(self):
        """ Store the average price of the move on the move and product form (costing method 'real')"""
        for move in self.filtered(lambda move: move.product_id.cost_method == 'fifo'):
            # product_obj = self.pool.get('product.product')
            if move.product_qty <= 0 or move.product_qty == 0:
                # if there is a negative quant, the standard price shouldn't be updated
                return
            # Note: here we can't store a quant.cost directly as we may have moved out 2 units
            # (1 unit to 5€ and 1 unit to 7€) and in case of a product return of 1 unit, we can't
            # know which of the 2 costs has to be used (5€ or 7€?). So at that time, thanks to the
            # average valuation price we are storing we will valuate it at 6€
            valuation_price = sum(m.price_unit * m.product_qty for m in move)
            average_valuation_price = valuation_price / move.product_qty

            move.product_id.with_context(force_company=move.company_id.id).sudo().write(
                {'standard_price': average_valuation_price})
            move.write({'price_unit': average_valuation_price})

        for move in self.filtered(
                lambda move: move.product_id.cost_method != 'fifo' and not move.origin_returned_move_id):
            # Unit price of the move should be the current standard price, taking into account
            # price fluctuations due to products received between move creation (e.g. at SO
            # confirmation) and move set to done (delivery completed).
            move.write({'old_price_unit': move.price_unit, 'price_unit': move.product_id.standard_price})
