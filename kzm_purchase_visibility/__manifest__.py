# -*- coding: utf-8 -*-
{
    'name': "Kzm Purchase Visibility",

    'summary': """
        """,

    'description': """
       Ajoute le group afficher les informations de l'achat
    """,

    'author': "Karizma",
    'website': "http://www.karizma.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'purchase',
                'account',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}