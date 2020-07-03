# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from lxml import etree
import json


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
    street = fields.Char("Address")
    email = fields.Char("Email")
    vat = fields.Char("VAT")
    legal_form = fields.Selection([
        ('anonimous', "Anonimous Society"),
        ('limited', "Limited Liability Company"),
        ('limited_prt', "Limited partnership"),
    ], default='anonimous')
    site_web = fields.Char("Web Site")
    file = fields.Binary(string='Terms and Conditions', attachement=True)
    file_sec = fields.Binary(string='Financial Information', attachement=True)
    # nature_type_tags = fields.Many2many('partner.supplier.type', string="Tags")
    file_name = fields.Char("File Name")
    file_name_sec = fields.Char("File Name")
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
        ('refused', "Refused"),
    ], default='draft', track_visibility='onchange')

    @api.constrains('file')
    def _check_file(self):
        if str(self.file_name.split(".")[1]) != 'pdf':
            raise exceptions.ValidationError("Cannot upload file different from .pdf file")

    @api.constrains('file_sec')
    def _check_file(self):
        if str(self.file_name_sec.split(".")[1]) != 'pdf':
            raise exceptions.ValidationError("Cannot upload file different from .pdf file")

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('ref.res') or 'REF'
        vals['name'] = seq
        return super(ResRef, self).create(vals)

    def action_draft(self):
        self.state = 'draft'

    def action_confirm(self):
        self.state = 'confirmed'

    def action_refuse(self):
        self.state = 'refused'

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
            # 'customer': not test,
            'company_id': self.company_id.id,
            'isReferenced': True,
            'reference_id': self.id,
        })

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

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(res_name)',
         "The name  must be unique"),
    ]

    no_update = fields.Boolean(string="Cannot update", compute='_check_update')

    def _check_update(self):
        for r in self:
            no_update = (r.state not in ['draft']) and not self.env.user.has_group(
                'kzm_referencement_v.group_ref_manager')
            r.no_update = no_update

    no_update_approved = fields.Boolean(string="Cannot update approved", compute='_check_approved')

    def _check_approved(self):
        for r in self:
            no_update_approved = (r.state not in ['draft', 'confirmed', 'refused'])
            r.no_update_approved = no_update_approved

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ResRef, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)

        if view_type in ['form']:  # Applies only for form view
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field"):  # All the view fields to readonly
                if node.get('name', 'TTTT'):
                    print("==========",node.get('name', 'TTTT'))
                    modifiers = json.loads(node.get("modifiers"))
                    print("********************", modifiers)
                    modifiers['readonly'] = ['|',('no_update', '=', True),('no_update_approved', '=', True)]
                    print("**********2222**********", modifiers)
                    node.set("modifiers", json.dumps(modifiers))
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    # @api.model
    # def fields_view_get2(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(ResRef, self).fields_view_get2(view_id=view_id, view_type=view_type, toolbar=toolbar,
    #                                                   submenu=submenu)
    #
    #     if view_type in ['form']:  # Applies only for form view
    #         doc = etree.XML(res['arch'])
    #         for node in doc.xpath("//field"):  # All the view fields to readonly
    #             if node.get('name', 'TTTT'):
    #                 modifiers = json.loads(node.get("modifiers"))
    #                 modifiers['readonly'] = [('no_update_approved', '=', True)]
    #                 node.set("modifiers", json.dumps(modifiers))
    #         res['arch'] = etree.tostring(doc, encoding='unicode')
    #     return res
