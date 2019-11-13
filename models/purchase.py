# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from odoo.addons import decimal_precision as dp

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _default_account_analytic_id(self):
        cuenta_analitica= self.env.user.account_analytic_id
        return cuenta_analitica

    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account', default = _default_account_analytic_id )
    ref_product_uom = fields.Many2one('product.uom', string='UdM ref.')
    ref_product_qty = fields.Float(string='Cantidad ref.', digits=dp.get_precision('Product Unit of Measure'))
    
