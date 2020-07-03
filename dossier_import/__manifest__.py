# -*- coding: utf-8 -*-

{
    "name": "Dossier Import",
    "version": "12.1",
    "depends": ["sale","purchase","account","stock","stock_account"],
    "author": "KARIZMA CONSEIL",
    'website': 'https://karizma-conseil.com',
    "category": "",
    "description": "Dossier import",
                        
    "init_xml": [],
    'data': [
        "security/account_security.xml",
        'security/ir.model.access.csv',
        'views/dossier_import.xml',
        'wizard/dossier_import_wizard_view.xml',
        'views/dossier_import_sequence.xml',
        'views/product_view.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
