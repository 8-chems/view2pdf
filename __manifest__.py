# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Web',
    'category': 'Hidden',
    'version': '1.0',
    'description':
        """
Odoo Web module.
========================
This module provides the ability to print Odoo views.
        """,
    'depends': ['base'],
    'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'reports/styles_insertion.xml',
        'reports/view_report_to_pdf_generator.xml',
        'reports/custom_header/view_report_custom_external_layout.xml',
        'reports/custom_header/view2pdf_custom_external_layout_standard.xml'
    ],
    'qweb': [],
    'bootstrap': True,  # load translations for login screen
}
