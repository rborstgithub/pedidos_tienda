# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class StockMove(models.Model):
    _inherit = "stock.move"

    ref_product_uom_qty = fields.Float(related="purchase_line_id.ref_product_qty", string='Cantidad ref.', readonly=True)
    ref_product_uom = fields.Many2one(related="purchase_line_id.ref_product_uom", string='UdM ref.', readonly=True)
