# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models


class ir_model(models.Model):

    _inherit = "ir.model"

    def init(self):
        cr = self._cr
        models = [
            'product.category',
            'product.attribute',
            'uom.categ',
            'uom.uom',
            'product.template',
            'product.supplierinfo',
            'product.pricelist',
            'product.pricelist.item',
            'product.product',
            'res.country',
            'res.country.state',
            'res.partner',
            'res.partner.bank',
            'res.partner.category',
            'res.partner.title',
            'res.bank',
        ]
        except_groups = [  # Group that won't be readonly
            'Administrateur des articles',
            'Administrateur des clients/Fournisseurs',
        ]
        # Update all models to be readonly first
        query = """
            update ir_model_access
            set  perm_read = True, perm_write = False, perm_unlink = False, perm_create = False
            where
            group_id not in (select id from res_groups where name in
            %s)
            and model_id in (select id from ir_model where model in %s)
        """
        cr.execute(query, (tuple(except_groups), tuple(models)))

ir_model()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
