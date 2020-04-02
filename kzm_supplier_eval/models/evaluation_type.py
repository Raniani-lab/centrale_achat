# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EvaluationType(models.Model):
    """represent the type of an evaluation, depending on the profile of the user the type contains many criterias"""

    _name = 'evaluation.type'
    _description = "Evaluation Types"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string=" Evaluation Type", required=True)
    description = fields.Text(string="Describe the type of evaluation")
    criterias_ids = fields.One2many('evaluation.criteria', 'evaluation_type_id', string="Criterias")
    evaluation_weight = fields.Selection([
        (str(i), str(i)) for i in range(1, 6)
    ], default='1')
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('done', "Done"),
    ], default='draft', track_visibility='onchange')

    def action_draft(self):
        self.state = 'draft'

    def action_confirm(self):
        self.state = 'confirmed'

    def action_done(self):
        self.state = 'done'
        env = self.env['mail.followers']
        env.search([]).unlink()
        self.env['mail.followers'].create({
            'res_id': self.id,
            'res_model': 'evaluation.type',
            'partner_id': self.env.uid,
        })

    @api.model
    def default_get(self, fields):
        """to create a type directly from selected criterias"""
        res = super(EvaluationType, self).default_get(fields)
        request_line_ids = self.env.context.get('active_ids', False)
        res['criterias_ids'] = [(6, 0, request_line_ids)]
        return res

class ResPartner(models.Model):
    _inherit="res.partner"

    supplier = fields.Boolean(string="Is a Supplier")
