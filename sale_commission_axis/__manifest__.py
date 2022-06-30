# -*- coding: utf-8 -*-
{
    'name': "Sales Commission Based On Sale Order, Invoice, Payment, Products, Product Category, Product Margin",
    'summary': "Sales Commission, Calculate Sales Commission in odoo, Sales order commssion, payment commission, product commission, Sales Agent commission, sale commission, Product Margin commission, invoice commssion",
     'description': "Sales Commission Based On Sale Order, Invoice, Payment, Products, Product Category, Product Margin",
    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','account','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/sales_commission.xml',
        'views/view_res_config_setting.xml',
        'views/view_sale_commission.xml',
        'views/view_res_partner.xml',
        'views/view_sale_order.xml',
        'views/menu_dashboard.xml',
        'views/view_account_invoice.xml',
        'wizard/view_commission_wizard.xml',
        'report/commission_sale_report.xml',
        'report/commisison_report_template.xml',
    ],
        'assets': {
            'web.assets_qweb': [
                'sale_commission_axis/static/src/xml/dashboard.xml',
            ],
        'web.assets_backend': [
            'sale_commission_axis/static/src/js/dashboard.js',
            'sale_commission_axis/static/src/scss/style.scss',
            'sale_commission_axis/static/src/css/portal_helpdesk.css',
        ],
            'web.assets_frontend': [
                'sale_commission_axis/static/src/scss/style.scss',
                'sale_commission_axis/static/src/js/portal.js',

            ],

    },

   'qweb': ["static/src/xml/dashboard.xml"],
    'version': '14.0.0.1',   
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 59,
    'currency': 'USD',
    'category':'Dashboard',
    'support': 'business@axistechnolabs.com',
    'author': 'Axis Technolabs',
    'website': 'https://www.axistechnolabs.com',
    'images': ['static/description/images/Sales-commission.jpg'],

}
