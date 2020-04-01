# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class PurchaseRequest(models.Model):

    _inherit = 'purchase.request'

    assigned_to = fields.Many2one(
        'res.users', 'Approver',
        compute="_compute_approver",readonly=True
    )

    @api.multi
    @api.depends('requested_by')
    def _compute_approver(self):
        for rec in self:
            emp = rec.env['hr.employee'].search([('user_id', '=', rec.requested_by.id)], limit=1)
            if emp:
                rec.assigned_to = emp.parent_id.user_id.id


    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)
        for o in self:
            if o.assigned_to and o.assigned_to.partner_id:
                old_followers = self.env['mail.followers'].search(
                    [('res_id', '=', o.id), ('res_model', '=', 'purchase.request'), ('partner_id','in', [o.assigned_to.partner_id.id, o.requested_by.partner_id.id])])
                if old_followers:
                    old_followers.sudo().unlink()
                res = super(PurchaseRequest, self).write(vals)
                self.env['mail.followers'].create({
                    'res_id': o.id,
                    'res_model': 'purchase.request',
                    'partner_id': o.assigned_to.partner_id.id,
                })
            #if o.requested_by and o.requested_by.partner_id:
                self.env['mail.followers'].create({
                    'res_id': o.id,
                    'res_model': 'purchase.request',
                    'partner_id': o.requested_by.partner_id.id,
                })

        return res

    @api.multi
    def button_to_approve(self):
        res = super(PurchaseRequest, self).button_to_approve()
        self.activity_update()
        return res

    @api.multi
    def button_rejected(self):
        res = super(PurchaseRequest, self).button_rejected()
        self.activity_update()
        return res

    @api.model
    def create(self, vals):
        res = super(PurchaseRequest, self).create(vals)
        for o in self:
            if o.assigned_to and o.assigned_to.partner_id:
                old_followers = self.env['mail.followers'].search(
                    [('res_id', '=', o.id), ('res_model', '=', 'purchase.request'),('partner_id','in', [o.assigned_to.partner_id.id, o.requested_by.partner_id.id])])
                if old_followers:
                    old_followers.sudo().unlink()
                self.env['mail.followers'].create({
                    'res_id': o.id,
                    'res_model': 'purchase.request',
                    'partner_id': o.assigned_to.partner_id.id,
                })
                self.env['mail.followers'].create({
                    'res_id': o.id,
                    'res_model': 'purchase.request',
                    'partner_id': o.requested_by.partner_id.id,
                })
        return res

    def activity_update(self):
        to_clean, to_do = self.env['purchase.request'], self.env['purchase.request']
        for holiday in self:
            if holiday.state == 'draft':
                to_clean |= holiday
            elif holiday.state == 'to_approve':
                holiday.activity_schedule(
                    'kzm_purchase_request_validation.mail_act_purchase_approval',
                    user_id=holiday.assigned_to.id)

            elif holiday.state == 'approved':
                to_do |= holiday
            elif holiday.state == 'rejected':
                to_clean |= holiday
        if to_clean:
            to_clean.activity_unlink(['kzm_purchase_request_validation.mail_act_purchase_approval',])
        if to_do:
            to_do.activity_feedback(['kzm_purchase_request_validation.mail_act_purchase_approval',])



