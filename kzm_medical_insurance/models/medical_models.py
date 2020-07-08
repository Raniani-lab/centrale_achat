# -*- coding: utf-8 -*-
from odoo import api, models,fields,_


class MedicalRecordBenifit(models.Model):
    _name = 'medical.record.benefit'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Medical présentation", required= True)
    refund_rate = fields.Integer(string="Refund rate", required=True)
    upper_limit = fields.Float(string="Upper limit")
    currency_id = fields.Many2one ('res.currency', string="Currency")
    observation = fields.Text(string="Observation")
    record_type = fields.Many2one('medical.record.type')


class MedicalRecordType(models.Model):
    _name = 'medical.record.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Record Type", required = True)
    prestation_ids = fields.One2many('medical.record.benefit','record_type', string="Medical service")
    observation = fields.Text(string="Observation")

class MedicalRecord(models.Model):
    _name = 'medical.record'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Affiliation number", required= True , default="DM")
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("in_progress", "In progress"),
            ("expired", "Expired"),
            ("canceled", "Canceled"),
        ],
        default="new",
    )

    employee_id = fields.Many2one('hr.employee', string="Employee",required= True)
    departement_id =fields.Many2one('hr.department' ,string="Department")
    job_id = fields.Many2one('hr.job', string="Job",required= True)
    folder_type = fields.Many2one('medical.record.type', required= True)
    beneficiaries_ids = fields.One2many('hr.employee.dependent','medical_record_id')


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for r in self:
            if r.employee_id:
                r.job_id = r.employee_id.job_id
                r.departement_id = r.employee_id.department_id

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('medical.record') or 'DM'
        vals['name'] = seq
        return super(MedicalRecord, self).create(vals)

class MedicalRefundRequest(models.Model):
    _name = 'medical.refund.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("submited", "Submitted"),
            ("verified", "verified"),
            ("validated", "Validated"),
            ("refused", "Refused"),
        ],
        default="draft",
    )

    name = fields.Char(string="Number",required= True , default="DR")
    employee_id = fields.Many2one('hr.employee', required= True , string="Employee")
    adherent_folder = fields.Boolean(string="The file concerns the member", required= True, default= False)
    patient_full_name = fields.Many2one('hr.employee.dependent')
    contribution_amount = fields.Float(string="Caisse contribution amount")
    nature_of_the_disease = fields.Char(string="Disease nature", required = True)
    date = fields.Date(string="Date")
    medical_presentation_ids = fields.One2many('medical.refund.request.line','refund_request_id')
    medical_run_id = fields.Many2one('medical.refund.request.run',ondelete = "cascade")
    total = fields.Float(string="Total", compute="_compute_amount")
    difference = fields.Float(string="Difference")

    def _compute_amount(self):
        sum = 0
        for r in self:
            for line in r.medical_presentation_ids:
                sum += line.amount
            r.total = sum

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('medical.refund.request') or 'DR'
        vals['name'] = seq
        return super(MedicalRefundRequest, self).create(vals)


class MedicalRefundRequestLine(models.Model):
    _name = 'medical.refund.request.line'

    type_id = fields.Many2one('medical.record.benefit', required= True, string="Type")
    description = fields.Char(string="Description", required= True)
    amount = fields.Float(string="Amount", required= True)
    date = fields.Date(string="Date")
    attachment_ids = fields.Many2many('ir.attachment',string="Attachments")
    refund_request_id = fields.Many2one('medical.refund.request', ondelete = "cascade")

    difference = fields.Float(string="Difference")






class MedicalRefundRequestRun(models.Model):
    _name = 'medical.refund.request.run'

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("validated", "Validated"),
            ("refused", "Refused"),
        ],
        default="draft",
    )

    name = fields.Char("Number", required = True, default="LDR")
    period_id = fields.Many2one('date.range', string="period")
    date = fields.Date(string="Date")
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    refund_request_ids = fields.One2many('medical.refund.request','medical_run_id')
    total = fields.Float(string="Total" , compute="_compute_total")
    actual_sold = fields.Float(string="Actual Sold")
    diffrence = fields.Float(string="Difference")

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('medical.refund.request.run') or 'LDR'
        vals['name'] = seq
        return super(MedicalRefundRequestRun, self).create(vals)


    def _compute_total(self):
        sum = 0
        for r in self:
            for line in r.refund_request_ids:
                sum += line.amount
            r.total = sum
