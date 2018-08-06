# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

from odoo.addons import decimal_precision as dp
class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    location_ids = fields.Many2many('stock.location',string='Ubicacion')
    uom_id = fields.Many2one('product.uom','Unidad de medida')