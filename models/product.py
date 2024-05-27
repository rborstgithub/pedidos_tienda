# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class ProductProduct(models.Model):
    _inherit = "product.template"

    plantilla_id = fields.Many2one('pedidos_tienda.plantilla_producto', string='Plantilla')

class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    location_ids = fields.Many2many('stock.location',string='Ubicacion')
    uom_id = fields.Many2one('uom.uom','Unidad de medida')
