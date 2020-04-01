# -*- coding: utf-8 -*-
from odoo import http

# class KzmPurchaseRequestValidation(http.Controller):
#     @http.route('/kzm_purchase_request_validation/kzm_purchase_request_validation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kzm_purchase_request_validation/kzm_purchase_request_validation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kzm_purchase_request_validation.listing', {
#             'root': '/kzm_purchase_request_validation/kzm_purchase_request_validation',
#             'objects': http.request.env['kzm_purchase_request_validation.kzm_purchase_request_validation'].search([]),
#         })

#     @http.route('/kzm_purchase_request_validation/kzm_purchase_request_validation/objects/<model("kzm_purchase_request_validation.kzm_purchase_request_validation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kzm_purchase_request_validation.object', {
#             'object': obj
#         })