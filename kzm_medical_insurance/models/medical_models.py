# -*- coding: utf-8 -*-
from odoo import api, models,fields,_
from odoo.exceptions import ValidationError
from pprint import pprint



class MedicalRecordBenifit(models.Model):
    _name = 'medical.record.benefit'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Medical présentation", required= True)
    refund_rate = fields.Integer(string="Refund rate", required=True)
    is_capped= fields.Boolean(string="Is capped ?")
    upper_limit = fields.Float(string="Upper limit")
    periodicities = fields.Integer(string="Periodicities")
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
    #folder_type = fields.Many2one('medical.record.type', required= True)
    beneficiaries_ids = fields.One2many('hr.employee.dependent','medical_id')
    mutual_contract = fields.Many2one('medical.contract', string="Mutual Contract", required=True)
    refund_request_ids = fields.One2many('medical.refund.request', 'mutual_refund_id')
    hr_expense_id = fields.Many2one('hr.expense', string="Expense sheet")

    refund_count = fields.Integer(compute='_compute_refund_count', string='Refunds Count')

    def _compute_refund_count(self):
        for r in self:
            r.refund_count = self.env['medical.refund.request'].search_count([('mutual_refund_id', '=', r.id)])

    def see_medical_refunds(self):
        action = self.env.ref('kzm_medical_insurance.medical_refund_request_menu_8').read()[0]
        action['domain'] = [('id', 'in', self.refund_request_ids.ids)]
        if self.refund_request_ids:
            action['res_id'] = self.refund_request_ids[0].id
        else:
            action['context'] = {
                'default_mutual_refund_id': self.id,
                'default_employee_id': self.employee_id.id,

            }
        print("action   : ", action)
        return action


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

    @api.constrains('beneficiaries_ids')
    def define_age_and_number(self):
        for r in self:
            nuber_childs = 0
            for l in r.beneficiaries_ids:
                if l.type == "child":
                    nuber_childs += 1
                    if l.age > 23:
                        raise ValidationError(_("The benefeciaries can not be aged more than 23 years !"))
                    else:
                        continue
            if nuber_childs > 4 :
                raise ValidationError(_("The benefeciaries can not be more than four children!"))




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
    adherent_folder = fields.Boolean(string="The request concerns a depending memeber?", required= True, default= False)
    patient_full_name = fields.Many2one('hr.employee.dependent')
    #contribution_amount = fields.Float(string="Caisse contribution amount")
    nature_of_the_disease = fields.Char(string="Disease nature", required = True)
    date = fields.Date(string="Date")
    medical_presentation_ids = fields.One2many('medical.refund.request.line','refund_request_id')
    mutual_refund_id = fields.Many2one('medical.record')
    medical_run_id = fields.Many2one('medical.refund.request.run')
    hr_expense_id = fields.Many2one('hr.expense', string="Expense sheet")
    total = fields.Float(string="Total", compute="_compute_amount")
    hr_expense_ids = fields.One2many('hr.expense', 'medical_refund_expense_id')
    #difference = fields.Float(string="Difference")
    def _compute_amount(self):
        sum = 0
        for r in self:
            for line in r.medical_presentation_ids:
                sum += line.amount
            r.total = sum

    expense_count = fields.Integer(compute='_compute_expense_count', string='Expense Count')

    def _compute_expense_count(self):
        for r in self:
            r.expense_count = self.env['hr.expense'].search_count([('medical_refund_expense_id', '=', r.id)])

    def see_expense(self):
        action = self.env.ref('hr_expense.hr_expense_actions_my_unsubmitted').read()[0]
        action['domain'] = [('id', 'in', self.hr_expense_ids.ids)]
        print("tttttttttttttttttttttttttttttt",self.hr_expense_ids.ids)
        # if self.hr_expense_ids:
        #     action['res_id'] = self.hr_expense_ids[0].id
        # else:
        #     action['context'] = {
        #         'default_medical_refund_expense_id': self.id,
        #         'default_employee_id': self.employee_id.id,
        #
        #     }
        print("action   : ", action)
        return action

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('medical.refund.request') or 'DR'
        vals['name'] = seq
        return super(MedicalRefundRequest, self).create(vals)

    def submit_action(self):
        self.state = 'submited'

    def verify_action(self):
        self.state = 'verified'

    def refuse_action(self):
        self.state = 'refused'

    def draft_action(self):
        self.state = 'draft'


class MedicalRefundRequestLine(models.Model):
    _name = 'medical.refund.request.line'

    type_id = fields.Many2one('medical.record.benefit', required= True, string="Type")
    description = fields.Char(string="Description", required= True)
    amount = fields.Float(string="Amount", required= True)
    date = fields.Date(string="Date")
    attachment_ids = fields.Many2many('ir.attachment',string="Attachments")
    refund_request_id = fields.Many2one('medical.refund.request', ondelete = "cascade")

    #difference = fields.Float(string="Difference")






class MedicalRefundRequestRun(models.Model):
    _name = 'medical.refund.request.run'

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("validated", "Validated"),
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
    diffrence = fields.Float(string="Difference" , compute="_compute_diff")

    @api.depends('actual_sold','total')
    def _compute_diff(self):
        for r in self:
            r.diffrence = r.actual_sold - r.total

    #expences_ids = fields.Many2many('hr.expense', compute="_compute_expense_ids", string="Expenses", medical.contract=True)
    #
    # @api.depends('refund_request_ids')
    # def _compute_expense_ids(self):
    #     for r in self:
    #         expenses = []
    #         for expense in r.refund_request_ids:
    #             if expense.medical_run_id:
    #                 expenses.append(expense.medical_run_id.id)
    #         r.expences_ids = [(6, 0, expenses)]

    refund_count = fields.Integer(compute='_compute_refund_count', string='Refunds Count')

    def _compute_refund_count(self):
        for r in self:
            r.refund_count = self.env['medical.refund.request'].search_count([('mutual_refund_id', '=', r.id)])

    def see_medical_refunds(self):
            action = self.env.ref('kzm_medical_insurance.medical_refund_request_menu_8').read()[0]
            action['domain'] = [('id', 'in', self.refund_request_ids.ids)]
            if self.refund_request_ids:
                action['res_id'] = self.refund_request_ids[0].id
            else:
                action['context'] = {
                    'default_medical_run_id': self.id,
                    #'default_employee_id': self.refund_request_ids.employee_id.id,

                }
            print("action   : ", action)
            return action


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('medical.refund.request.run') or 'LDR'
        vals['name'] = seq
        return super(MedicalRefundRequestRun, self).create(vals)


    def _compute_total(self):
        sum = 0
        for r in self:
            for line in r.refund_request_ids.medical_presentation_ids:
                sum += line.amount
            r.total = sum

    def validate_action(self):
        self.generate_expense()
        self.state = 'validated'

    def generate_expense(self):
        for r in self:
            for l in r.refund_request_ids:
                data = {
                    'name': l.name,
                    'product_id': l.env.company.expense_medical_product_id.id,
                    'employee_id': l.employee_id.id,
                    'medical_refund_expense_id': l.id,
                    'unit_amount': l.total,
                }
                #data['expenses_ids'] = [(4, l.medical_run_id.id)]
                print("+++++++++++++++++++++++++++++++++++++++++++++++++")
                pprint(data)
                expense = self.env['hr.expense'].create(data)
                print("====================================", expense.id)
                data = {
                    'name': expense.name,
                    'employee_id': expense.employee_id.id,

                    'expense_line_ids':[(4, expense.id)],

                }
                expens_sheet = self.env['hr.expense.sheet'].create(data)
                expens_sheet.action_submit_sheet()
                expens_sheet.approve_expense_sheets()


    def draft_action(self):
        self.state = 'draft'



class MedicalContract (models.Model):
    _name = 'medical.contract'

    name = fields.Char("Number", required=True, default="CM")
    contract_name = fields.Char("Name", required=True)
    performance_matrix_id = fields.Many2one('medical.record.type')
    employee_categ_ids = fields.One2many('hr.category.medical.line', 'medical_contract_id')
    medical_record_ids = fields.One2many('medical.record', 'mutual_contract',string="Medical record")

    records_count = fields.Integer(compute='_compute_records_count', string='Records Count')

    def _compute_records_count(self):
        for r in self:
            r.records_count = self.env['medical.record'].search_count([('mutual_contract', '=', r.id)])
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('medical.contract') or 'CM'
        vals['name'] = seq
        return super(MedicalContract, self).create(vals)

    def see_medical_records(self):
        action = self.env.ref('kzm_medical_insurance.medical_record_menu_8').read()[0]
        action['domain'] = [('id', 'in', self.medical_record_ids.ids)]
        if self.medical_record_ids:
            action['res_id'] = self.medical_record_ids[0].id
        else:
            action['context'] = {
                'default_mutual_contract': self.id,
                'default_employee_id': self.user_id.id,

            }
        print("action   : ", action)
        return action

    category_ids = fields.Many2many('hr.category', compute="_compute_category_ids", string="Categories", store=True)

    @api.depends('employee_categ_ids')
    def _compute_category_ids(self):
        for r in self:
            categories = []
            for category in r.employee_categ_ids:
                if category.category_id:
                    categories.append(category.category_id.id)
            r.category_ids = [(6, 0, categories)]

class HrMedicalCategoryLine(models.Model):
    _name = 'hr.category.medical.line'

    medical_contract_id = fields.Many2one('medical.contract')
    category_id = fields.Many2one('hr.category')


# class HrContractCategory(models.Model):
#     _inherit = 'hr.category'
#
#     medical_contract_id = fields.Many2one('medical.contract')


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    medical_refund_expense_id = fields.Many2one('medical.refund.request')

class HrEmployeeDependent(models.Model):
    _inherit = 'hr.employee.dependent'

    medical_record_id = fields.Many2one('medical.record')
    medical_id = fields.Many2one('medical.record')