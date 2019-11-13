# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class ConversionUnidadMedida(models.Model):
    _name = 'pedidos_tienda.conversion_uom'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', 'Producto')
    uom_id = fields.Many2one('product.uom', 'Unidad medida origen', required=True)
    uom_dest_id = fields.Many2one('product.uom', 'Unidad medida destino', required=True)
    factor = fields.Float('Factor conversión', required=True)
    
    
