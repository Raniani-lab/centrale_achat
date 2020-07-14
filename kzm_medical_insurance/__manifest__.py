# -*- coding: utf-8 -*-
{
    'name': "Kzm Medical Insurance",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "Karizma-conseil",
    'website': "http://www.karizma_conseil.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'hr',
                'isesco_hr',
                'date_range',
                'kzm_account_fiscalyear_type',
                'hr_expense',
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/data_setting.xml',
        'views/medical_record.xml',
        'views/medical_contract.xml',
        'views/medical_record_benifit.xml',
        'views/medical_record_type.xml',
        'views/medical_refund_request.xml',
        'views/medical_refund_request_run.xml',
        'views/res_config_settings.xml',
        'views/menu.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
