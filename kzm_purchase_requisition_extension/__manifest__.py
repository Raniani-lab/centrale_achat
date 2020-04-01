# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "KZM Purchase Requisition Extension",
    "author": "KARIZMA",
    "version": "12.0.1.0.0",
    "summary": "Use this module to compare request for quotations.",
    "category": "Purchase Management",
    "depends": [
        "purchase_requisition"
    ],
    "data": [
        "reports/report_purchaserequisition_comparative.xml",
        "views/purchase_request_report.xml",
    ],
    'demo': [
    ],
    "license": 'LGPL-3',
    'installable': True,
    'application': True,
}
