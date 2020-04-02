# -*- coding: utf-8 -*-
from datetime import timedelta, date
from odoo import tools
from odoo import models, fields, api, exceptions, _


class EvaluationEvaluation(models.Model):
    """ Represente levaluation du fournisseur """

    _name = 'evaluation.evaluation'
    _description = "Evaluations"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    description = fields.Text()
    start_date = fields.Datetime(default=fields.Datetime.today(), string="Evaluation Confirmation Date")
    name = fields.Char(string="Evaluation Title", default = 'EVALUATION DE')
    evaluation_deadline_date = fields.Date(string="Evaluation Deadline")
    evaluation_note = fields.Float(string="Evaluation note", compute='_compute_evaluation_note')
    evaluation_responsible_id = fields.Many2one('res.users',
                                                string="Evaluation Responsible",
                                                compute='_compute_approver')
    evaluation_type_id = fields.Many2one('evaluation.type', string="Type of Evaluation")
    current_user = fields.Many2one('res.users', 'Evaluator', default=lambda self: self.env.uid)
    evaluation_line_ids = fields.One2many('evaluation.line', 'evaluation_id', string="Evaluation Lines")
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Orders Evaluated")
    coef_sum = fields.Char(string="Total scale", compute='_compute_evaluation_note')
    supplier_id = fields.Many2one('res.partner', string="Supplier Evaluated", compute='_get_supplier_id')
    color = fields.Integer()
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('done', "Done"),
    ], default='draft', track_visibility='onchange')

    @api.onchange('purchase_order_id')
    def _get_supplier_id(self):
        """permet de charger automatiquement le fournisseur une fois que le
        bon de commande est choisis"""
        for r in self:
            r.supplier_id = r.purchase_order_id.partner_id.id

    @api.onchange('evaluation_type_id')
    def _get_eval_lines(self):
        """permet de creer les lignes devaluations suivant le type devaluation en se basant sur les criteres"""
        for o in self:
            to_be_creat = []
            for c in o.evaluation_type_id.criterias_ids:
                to_be_creat.append((0, 0, {
                    'criteria_id': c.id,
                    'evaluation_id': o.id,
                }))
            o.evaluation_line_ids = to_be_creat

    def action_draft(self):
        self.state = 'draft'

    def action_confirm(self):
        self.state = 'confirmed'

    def action_done(self):
        self.state = 'done'
        old_followers = self.env['mail.followers'].search(
            [('res_id', '=', self.id),
             ('res_model', '=', 'evaluation.evaluation'),
             ])
        if old_followers:
            old_followers.sudo().unlink()
        admin = self.env['res.users'].search([('name', '=', 'Administrator')])
        self.env['mail.followers'].create({
            'res_id': self.id,
            'res_model': 'evaluation.evaluation',
            'partner_id': admin.partner_id.id,
        })
        if self.evaluation_responsible_id.id != admin.id and self.evaluation_responsible_id.id != self.current_user:
            self.env['mail.followers'].create({
                'res_id': self.id,
                'res_model': 'evaluation.evaluation',
                'partner_id': self.evaluation_responsible_id.partner_id.id,
            })

    @api.depends('current_user')
    def _compute_approver(self):
        for rec in self:
            emp = rec.env['hr.employee'].search([('user_id', '=', rec.current_user.id)], limit=1)
            if emp.parent_id.user_id.id:
                # Veuillez checker que le user responsable a un partenaire associe deja creer
                rec.evaluation_responsible_id = emp.parent_id.user_id.id
            elif rec.current_user.has_group('kzm_supplier_eval.group_eval_manager'):
                rec.evaluation_responsible_id = rec.current_user.id
            else:
                admin = rec.env['res.users'].search([('name', '=', 'Administrator')])
                rec.evaluation_responsible_id = admin.id

    @api.onchange('evaluation_line_ids')
    def _compute_evaluation_note(self):
        """Calcule la note totale de levaluation a chaque modification des lignes devaluations"""
        for o in self:
            notes = sum([int(l.note_with_coef) for l in o.evaluation_line_ids or []])
            coefs = sum([int(l.criteria_id.criteria_coef) for l in o.evaluation_line_ids or []])
            o.coef_sum = str(coefs)
            o.evaluation_note = round(notes / (coefs or 1.0), 2)


class EvaluationLine(models.Model):
    """Represente les lignes devaluations contenues dans la classe de levaluations"""

    _name = 'evaluation.line'
    _description = "Evaluations Lines"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    evaluation_comments = fields.Text(string="Comments")
    note_without_coef = fields.Selection([
        (str(i), str(i)) for i in range(1, 6)
    ], string="Note")
    criteria_id = fields.Many2one('evaluation.criteria', string="")
    evaluation_id = fields.Many2one('evaluation.evaluation', string="")
    note_with_coef = fields.Integer(string="Note*Coef", compute='_compute_note_with_coef', store="True")
    criteria_coef = fields.Char(string="Coef", compute='_get_criteria_coef')

    @api.depends('note_without_coef')
    def _compute_note_with_coef(self):
        """calcule la note ponderee pour chaque ligne devaluation au changement de la note simple"""
        for r in self:
            r.note_with_coef = int(r.note_without_coef)*int(r.criteria_id.criteria_coef)

    @api.depends('criteria_id')
    def _get_criteria_coef(self):
        """ recupere le coef du critere"""
        for r in self:
            r.criteria_coef = str(r.criteria_id.criteria_coef) if r.criteria_id else None