# -*- coding: utf-8 -*-
{
    'name': "Kzm Purchase Restriction",

    'summary': """
        Purchase Restriction""",

    'description': """
        
    """,

    'author': "Karizma Conseil",
    'website': "http://www.karizma-conseil.com",

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
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}