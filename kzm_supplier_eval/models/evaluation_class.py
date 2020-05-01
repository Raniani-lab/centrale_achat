# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime
from odoo import models, fields, api, _


class EvaluationClass(models.Model):
    """Représente les classes de fournisseurs paramétrable en fonction de la note maximale et de la minimale"""
    _name = 'evaluation.class'
    _description = "Supplier Class"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char(string="Evaluations Classes", required=True)
    description = fields.Text()
    note_max = fields.Float(string="Max mark", required=True)
    note_min = fields.Float(string="Min mark", required=True)
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
            'res_model': 'evaluation.class',
            'partner_id': self.env.uid,
        })


class Partner(models.Model):
    """Représente les fournisseurs modifiés, en ajoutant un parametre classe de fournisseur et sa note"""

    _inherit = 'res.partner'
    evaluation_class_id = fields.Many2one('evaluation.class',
                                          string="Classe du fournisseur", compute='_get_supplier_class')
    evaluation_class_name = fields.Char(string="Designation Classe du fournisseur", compute='_get_supplier_class')
    evaluation_note = fields.Float(string="Note du fournisseur", compute='_compute_global_note')
    evaluation_ids = fields.One2many('evaluation.evaluation', 'supplier_id', compute='_compute_global_note')
    evaluation_inv_ids = fields.One2many('evaluation.evaluation', 'supplier_id_inv', compute='_compute_global_note')
    evaluation_rec_ids = fields.One2many('evaluation.evaluation', 'supplier_id_rec', compute='_compute_global_note')
    evaluations = fields.One2many('evaluation.evaluation', 'supplier_eval')

    def _compute_global_note(self):
        """calculer la note globale du fournisseurs en considérant toutes les évaluations faites sur le fournisseur
        pour les 6 derniers mois"""
        for r in self:
            date_max = datetime.today() - timedelta(6 * 365 / 12)
            po = r.env['purchase.order'].search([('partner_id', '=', r.id)])
            po_inv = r.env['account.move'].search([('partner_id', '=', r.id)])
            po_rec = r.env['stock.picking'].search([('partner_id', '=', r.id)])
            # timedelta(minutes=60) juste pour tester que le code prends vraiment en consideration la duree
            evals = r.env['evaluation.evaluation'].search(['&', ('purchase_order_id', 'in', [p.id for p in po])
                                                              , ('start_date', '>', date_max)])
            evals_inv = r.env['evaluation.evaluation'].search(['&', ('invoice_id', 'in', [p.id for p in po_inv])
                                                                  , ('start_date', '>', date_max)])
            evals_rec = r.env['evaluation.evaluation'].search(['&', ('receipt_id', 'in', [p.id for p in po_rec])
                                                                  , ('start_date', '>', date_max)])
            r.evaluation_ids = evals
            r.evaluation_inv_ids = evals_inv
            r.evaluation_rec_ids = evals_rec

            notes = sum([l.evaluation_note * int(l.evaluation_type_id.evaluation_weight) for l in evals])
            notes_inv = sum([l.evaluation_note * int(l.evaluation_type_id.evaluation_weight) for l in evals_inv])
            notes_rec = sum([l.evaluation_note * int(l.evaluation_type_id.evaluation_weight) for l in evals_rec])
            note_all = [notes, notes_inv, notes_rec]
            total_all = sum(note_all)

            coefs = sum([int(l.evaluation_type_id.evaluation_weight) for l in evals])
            coefs_inv = sum([int(l.evaluation_type_id.evaluation_weight) for l in evals_inv])
            coefs_rec = sum([int(l.evaluation_type_id.evaluation_weight) for l in evals_rec])
            coef_all = [coefs, coefs_inv, coefs_rec]
            total_coef = sum(coef_all)

            r.evaluation_note = total_all / (total_coef or 1.0)
            print(r.evaluation_note)

    def _get_supplier_class(self):
        """récupère la classe fournisseur et l'affecte au fournisseurs pour affichage"""
        for r in self:
            classe = self.env['evaluation.class'].search(['&', ('note_max', '>=', r.evaluation_note)
                                                             , ('note_min', '<', r.evaluation_note)])
            r.evaluation_class_id = classe
            r.evaluation_class_name = "Classe " + classe.name if classe else None
            print(r.evaluation_class_name)

    def eval_recap(self):
        """action de redirection vers la liste des evaluations """
        po = self.env['purchase.order'].search([('partner_id', '=', self.id)])
        po_inv = self.env['account.move'].search([('partner_id', '=', self.id)])
        po_rec = self.env['stock.picking'].search([('partner_id', '=', self.id)])

        evals_recaps = self.env['evaluation.evaluation'].search([('purchase_order_id', 'in', [p.id for p in po])])
        evals_recaps_inv = self.env['evaluation.evaluation'].search([('invoice_id', 'in', [p.id for p in po_inv])])
        evals_recaps_rec = self.env['evaluation.evaluation'].search([('receipt_id', 'in', [p.id for p in po_rec])])
        action = self.env.ref('kzm_supplier_eval.evaluation_list_action').read()[0]
        tab = [len(evals_recaps), len(evals_recaps_inv), len(evals_recaps_rec)]
        total = sum(tab)
        if total > 1:
            action['domain'] = [('id', 'in', self.evaluations.ids)]

        elif total == 1:
            action['views'] = [(self.env.ref('kzm_supplier_eval.evaluation_form_view').id, 'form')]
            if len(evals_recaps) == 1:
                action['res_id'] = evals_recaps.id
            elif len(evals_recaps_inv) == 1:
                action['res_id'] = evals_recaps_inv.id
            else:
                action['res_id'] = evals_recaps_rec.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def supplier_class(self):
        """action de redirection vers le formulaire classe de fournisseur precis"""

        evals_class = self.env['evaluation.class'].search([('id', '=', self.evaluation_class_id.id)])
        action = self.env.ref('kzm_supplier_eval.evaluation_class_list_action').read()[0]
        if len(evals_class) > 1:
            action['domain'] = [('id', 'in', evals_class.ids)]
        elif len(evals_class) == 1:
            action['views'] = [(self.env.ref('kzm_supplier_eval.evaluation_class_form_view').id, 'form')]
            action['res_id'] = evals_class.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
