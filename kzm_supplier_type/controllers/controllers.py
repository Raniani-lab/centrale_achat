# -*- coding: utf-8 -*-
# from odoo import http


# class KzmSupplierType(http.Controller):
#     @http.route('/kzm_supplier_type/kzm_supplier_type/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kzm_supplier_type/kzm_supplier_type/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kzm_supplier_type.listing', {
#             'root': '/kzm_supplier_type/kzm_supplier_type',
#             'objects': http.request.env['kzm_supplier_type.kzm_supplier_type'].search([]),
#         })

#     @http.route('/kzm_supplier_type/kzm_supplier_type/objects/<model("kzm_supplier_type.kzm_supplier_type"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kzm_supplier_type.object', {
#             'object': obj
#         })
