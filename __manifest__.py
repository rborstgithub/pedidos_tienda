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
    'version': '0.2',

    'depends': ['purchase','pos_gt'],

    'data': [
        'views/views.xml',
        'views/product_views.xml',
        'views/partner_view.xml',
        'views/purchase_views.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
        'views/pedidos_tienda_view.xml',
        'security/ir.model.access.csv',
    ],
}
