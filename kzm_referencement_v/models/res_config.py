# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # approb_def1 = fields.Boolean("Default approbation", related='company_id.approb_def1', readonly=False)
    default_ref_responsible = fields.Many2one('res.users', default_model='ref.res', string="Approver")

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()


class ResCompany(models.Model):
    _inherit = "res.company"

    approb_def1 = fields.Boolean("Default approbation")

