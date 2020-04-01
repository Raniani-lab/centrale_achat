# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Type',
    'version': '0.1',
    "author": "Karizma",
    'category': 'Purchase Management',
    'website': 'http://www.karizma-conseil.com',
    'summary': 'Purchase Type (Import/Local)',
    'depends': [
        'purchase',
        'purchase_landed_cost'
    ],
    'data': [
        'security/purchase_type_security.xml',
        'views/purchase_order_view.xml',
    ],
    'installable': False,
    'images': [
    ],
    'license': 'AGPL-3',
}
