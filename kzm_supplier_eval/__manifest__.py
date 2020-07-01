# -*- coding: utf-8 -*-
{
    'name': "kzm supplier eval",

    'summary': """
        Supplier Evaluation based on Criterias and defined type of Evaluation""",

    'description': """
        Supplier Evaluation
    """,

    'author': "Assabe POLO, KARIZMA Conseil",
    'website': "http://www.karizma-conseil.com",
    # any module necessary for this oThree 6 Mafiane to work correctly
    'depends': ['base',
                'hr',
                'purchase'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/evaluation_view.xml',
        'views/evaluation_type_view.xml',
        'views/evaluation_criteria_view.xml',
        'views/evaluation_class_view.xml',
        'views/supplier_evaluated.xml',
        'report/evaluation_report.xml',
        'report/evaluation_evaluation_report.xml',
    ],
}