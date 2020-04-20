# -*- coding: utf-8 -*-
from odoo import http

# class KzmSupplierEval(http.Controller):
#     @http.route('/kzm_supplier_eval/kzm_supplier_eval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kzm_supplier_eval/kzm_supplier_eval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kzm_supplier_eval.listing', {
#             'root': '/kzm_supplier_eval/kzm_supplier_eval',
#             'objects': http.request.env['kzm_supplier_eval.kzm_supplier_eval'].search([]),
#         })

#     @http.route('/kzm_supplier_eval/kzm_supplier_eval/objects/<model("kzm_supplier_eval.kzm_supplier_eval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kzm_supplier_eval.object', {
#             'object': obj
#         })