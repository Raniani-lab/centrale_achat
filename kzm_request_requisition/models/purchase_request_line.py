
from datetime import datetime

from odoo import _, api, fields, models, exceptions
from odoo.exceptions import UserError


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    status = fields.Selection([('eligible', 'Eligible'), ('not_eligible', 'Not Eligible')], string='Status',
                              readonly=True)
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        track_visibility="onchange",
        required=True
    )

    @api.onchange('analytic_account_id', 'estimated_cost')
    def onchange_analytic_account_status(self):
        for o in self:
            if o.analytic_account_id:
                budget_line = self.env["crossovered.budget.lines"].search([("analytic_account_id", "=", o.analytic_account_id.id)])
                print(budget_line.planned_amount)
                if budget_line:
                    if (budget_line.date_from <= fields.Date.today() <= budget_line.date_to) and o.estimated_cost <= budget_line.planned_amount:
                        o.status = 'eligible'
                    else:
                        o.status = 'not_eligible'


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    def button_to_approve(self):
        self.to_approve_allowed_check()
        for o in self:
            for item in o.line_ids:
                if item.status == 'not_eligible':
                    raise UserError(_(
                        "The cost for the product '%s' exceed the allowed in the budget.") % item.product_id.name)
                else:
                    return self.write({"state": "to_approve"})



