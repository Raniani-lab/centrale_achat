# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EvaluationCriteria(models.Model):
    """ represent the criteria of the evaluation,
    it define the ligne of an evaluation and is associed to a type of evaluation"""

    _name = 'evaluation.criteria'
    _description = "Evaluation Criterias"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Criteria", required=True)
    description = fields.Text()
    sequence = fields.Integer(string='Sequence', default=10)
    evaluation_type_id = fields.Many2one('evaluation.type', string="Evaluator Type")
    current_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.uid)
    criteria_coef = fields.Selection([
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
            'res_model': 'evaluation.criteria',
            'partner_id': self.env.uid,
        })
