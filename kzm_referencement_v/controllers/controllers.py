# -*- coding: utf-8 -*-
from odoo import http

# class KzmReferencementV(http.Controller):
#     @http.route('/kzm_referencement_v/kzm_referencement_v/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kzm_referencement_v/kzm_referencement_v/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('kzm_referencement_v.listing', {
#             'root': '/kzm_referencement_v/kzm_referencement_v',
#             'objects': http.request.env['kzm_referencement_v.kzm_referencement_v'].search([]),
#         })

#     @http.route('/kzm_referencement_v/kzm_referencement_v/objects/<model("kzm_referencement_v.kzm_referencement_v"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kzm_referencement_v.object', {
#             'object': obj
#         })