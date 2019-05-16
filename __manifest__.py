# -*- coding: utf-8 -*-
{
    'name': "Pedidos Tienda",

    'summary': """Pedidos Tienda""",

    'description': """
        Pedidos Tienda
    """,

    'author': "aquíH",
    'website': "http://www.aquih.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['purchase','pos_gt'],

    'data': [
        'views/views.xml',
        'views/product_views.xml',
        'views/partner_view.xml',
        'security/ir.model.access.csv',
    ],
}
