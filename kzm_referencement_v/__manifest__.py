# -*- coding: utf-8 -*-
{
    'name': "kzm referencement v",

    'summary': """
        Referencement of products and suppliers""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Assabe POLO, karizma Conseil",
    'website': "https://karizma-conseil.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'product',
                'group_master',
                'account',
                ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/product_ref_view.xml',
        'views/product_template_view.xml',
        #'views/res_config_view.xml',
        'views/res_ref_view.xml',
        'views/menus.xml',
        'data/ref_seq.xml',
        'data/res_seq.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}