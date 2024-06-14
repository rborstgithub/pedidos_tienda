# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _plantilla(self):
        if self.order_line:
            plantillas = []
            for linea in self.order_line:
                if linea.product_id.plantilla_id and linea.product_id.plantilla_id.id not in plantillas:
                    plantillas.append(linea.product_id.plantilla_id.id)
            
            if len(plantillas) == 1:
                self.plantilla_id = self.order_line[0].product_id.plantilla_id
            else:
                self.plantilla_id = False
        else:
                self.plantilla_id = False

    plantilla_id = fields.Many2one('pedidos_tienda.plantilla_producto', string='Plantilla', compute='_plantilla')
