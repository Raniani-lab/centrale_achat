# -*- coding: utf-8 -*-
{
    'name': "Purchase Pequest Validation",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "Karizma",
    'website': "http://www.karizma.ma",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'purchase_request',
                'hr',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_request.xml',
        'data/mail_activity_data.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}