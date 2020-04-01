# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class ResRef(models.Model):
    _name = 'ref.res'
    _description = 'Referencement of clients and supplier'
    _inherit = ['ref.ref', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char("Ref sequence", default='New')
    res_name = fields.Char("Name")
    parent_id = fields.Many2one('res.partner')
    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual'), ('company', 'Company')],
                                    default='person')
    street = fields.Char("Street")
    vat = fields.Char("VAT")
    function = fields.Char("Function")
    phone = fields.Char("Phone")
    nature = fields.Selection([
        ('client', "Client"),
        ('supplier', "Supplier"),
    ], default='supplier', track_visibility='onchange')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Sent"),
        ('done', "Approved"),
    ], default='draft', track_visibility='onchange')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('ref.res') or 'REF'
        vals['name'] = seq
        return super(ResRef, self).create(vals)

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def action_done(self):
        self.state = 'done'
        test = True if self.nature == 'supplier' else False
        print(test)
        self.env['res.partner'].create({
            'name': self.res_name,
            'parent_id': self.parent_id.id,
            'company_type': self.company_type,
            'street': self.street,
            'vat': self.vat,
            'function': self.function,
            'phone': self.phone,
            'supplier': test,
            'customer': not test,
            'company_id': self.company_id.id,
            'isReferenced': True,
            'reference_id': self.id,
        })

    @api.multi
    def res_ref(self):
        """action de redirection le produit reference """
        test = True if self.nature == 'supplier' else False
        evals_recaps = self.env['res.partner'].search(['&', ('name', '=', self.res_name), ('supplier', '=', test)])
        print(test)
        if test:
            action = self.env.ref('base.action_partner_supplier_form').read()[0]
            if len(evals_recaps) > 1:
                action['domain'] = [('id', 'in', evals_recaps.ids)]
            elif len(evals_recaps) == 1:
                action['views'] = [(self.env.ref('base.view_partner_form').id, 'form')]
                action['res_id'] = evals_recaps.id
            else:
                action = {'type': 'ir.actions.act_window_close'}
            print(action)
        else:
            action = self.env.ref('base.action_partner_customer_form').read()[0]
            if len(evals_recaps) > 1:
                action['domain'] = [('id', 'in', evals_recaps.ids)]
            elif len(evals_recaps) == 1:
                action['views'] = [(self.env.ref('base.view_partner_form').id, 'form')]
                action['res_id'] = evals_recaps.id
            else:
                action = {'type': 'ir.actions.act_window_close'}
                print(action)
        return action
