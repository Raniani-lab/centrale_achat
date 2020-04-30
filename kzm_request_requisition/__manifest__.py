# -*- coding: utf-8 -*-

{
    "name": "Kzm request requisition",
    "version": "13.0",
    "depends": ["purchase_request", "purchase_requisition", "kzm_supplier_type"],
    "author": "KARIZMA CONSEIL",
    'website': 'https://karizma-conseil.com',
    "category": "",
    "description": "Add contract in Multiple consultation in DP Generation",
                        
    "init_xml": [],
    'data': [
        "views/purchase_order_views.xml",
        "wizard/purchase_request_line_views_inherit.xml",
        "views/request_requesition_appel_offre_views.xml",
        "views/res_config_views.xml",
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
