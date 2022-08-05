# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'PoS Customizations',
    'version': '1.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'Customizations for Point of Sale',
    'description': """
        This module adds customized features to POS
    """,
    'data': [
        'views/pos_order_views.xml'
    ],
    'depends': ['point_of_sale'],
    'installable': True,
    'assets': {
        'point_of_sale.assets': [
            "pos_customizations/static/src/js/PaymentScreen.js",
            "pos_customizations/static/src/js/ProductScreen.js",
        ],

        'web.assets_qweb': [
            'pos_customizations/static/src/xml/*',
        ],
    }
}
