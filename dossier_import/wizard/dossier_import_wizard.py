# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class LandedCostWizard(models.TransientModel):
    _name = "landed.cost.wizard"
    _description = "Landed Cost Wizard"

    picking_ids = fields.Many2many("stock.picking", string="Stock Pickings")

    def _prepare_distribution_line(self, move):
        return {
            'dossier_id': self.env.context['active_id'],
            'move_id': move.id,
            'purchase_id':move.picking_id.purchase_id.id,
            'product_id':move.product_id.id,
            'ordered_qty': move.product_qty,
            'taux_douane':move.product_id.taux_douane,
            'prix_devise':move.purchase_line_id.price_unit,
            'montant_devise': move.purchase_line_id.price_unit * move.product_qty,
        }

    def action_import_picking(self):
        self.ensure_one()
        dossier_import_id = self.env['dossier_import'].browse(
            self.env.context['active_id'])
        previous_moves = dossier_import_id.mapped('line_achat_ids.move_id')
        for move in self.mapped('picking_ids.move_lines'):
            if move not in previous_moves:
                self.env['achat.line.dossier.import'].create(
                    self._prepare_distribution_line(move))
