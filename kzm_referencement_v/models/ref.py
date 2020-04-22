# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class Ref(models.Model):

    _name = 'ref.ref'
    _description = "Referencement informations"

    ref_date = fields.Date("Demand date", default=fields.Date.today())
    ref_val_date = fields.Date("Validation date")
    ref_asked_by = fields.Many2one('res.users', string="Requested by", default=lambda self: self.env.uid)
    ref_responsible = fields.Many2one('res.users', string="Responsible")
