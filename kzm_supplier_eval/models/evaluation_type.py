# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EvaluationType(models.Model):
    """represent the type of an evaluation, depending on the profile of the user the type contains many criterias"""

    _name = 'evaluation.type'
    _description = "Evaluation Types"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string=" Title ", required=True)
    type_evaluation = fields.Selection(string='Evaluation Type',
                                       selection=[('buyer', 'Buyer'), ('accountant', 'Accountant'),
                                                  ('storekeeper', 'StoreKeeper')],
                                       default='buyer')
    description = fields.Text(string="Describe the type of evaluation")
    # users_ids = fields.Many2many('res.users', string="Users", domain=lambda self: [
    #     ("groups_id", "=", self.env.ref("kzm_supplier_eval.group_eval_evaluator").id)])
    users_ids = fields.Many2many('res.users', 'user_evaluation_type',string="Users")
    current_user = fields.Many2one(string="current user", compute='get_current_user')
    criterias_ids = fields.One2many('evaluation.criteria', 'evaluation_type_id', string="Criterias")
    evaluation_weight = fields.Selection([
        (str(i), str(i)) for i in range(1, 6)
    ], default='1')
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
    ], default='draft', track_visibility='onchange')

    # @api.onchange('users_ids')
    # def onchange_users_id(self):
    #     user = self.env['res.users'].browse(self.env.uid)
    #     if user.has_group('group_eval_evaluator'):
    #         users_gr = self.env.ref("kzm_supplier_eval.group_eval_evaluator").users.id
    #     return {'domain': {'users_ids': [('id', 'in', users_gr.ids)]}}

    def get_current_user(self):
        return self.env['res.users'].browse(self.env.uid)

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
    _inherit = "res.partner"

    supplier = fields.Boolean(string="Is a Supplier")


class UserModel(models.Model):
    _inherit = "res.users"

    models_ids = fields.Many2many('evaluation.type',  'user_evaluation_type', string="Models Users")




