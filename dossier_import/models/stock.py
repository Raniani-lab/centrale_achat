# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        landed_cost = self.env.context.get('landed_cost', False)
        if landed_cost:
            dossier_import = self.env['dossier_import'].browse(landed_cost)
            if dossier_import:
                args += [('purchase_id', 'in', dossier_import.purchase_ids.ids)]
        return super(StockPicking, self)._search(args=args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
