# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Partner(models.Model):
    _inherit = 'res.partner'

    monto_minimo_compras = fields.Integer('Monto minimo de compras')
