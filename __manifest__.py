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

    'depends': ['purchase'],

    'data': [
        'views/views.xml',
        'views/product_views.xml',
        'security/ir.model.access.csv',
    ],
}
