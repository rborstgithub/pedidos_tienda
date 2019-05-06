# -*- encoding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
import base64
import datetime
import logging

class pedidos_tienda_orden_compra(models.TransientModel):
    _name = 'pedidos_tienda.orden_compra'

    def _default_productos(self):
        lista_productos = []
        ubicacion_usuario_actual = self.env.user.default_location_id.id
        productos = self.env['product.product'].search([])
        for producto in productos:
            lista_ubicaciones = {'uom_id':[]}
            for proveedor in producto.seller_ids:
                for ubicacion in proveedor.location_ids:
                    if ubicacion.id == ubicacion_usuario_actual:
                        lista_ubicaciones['uom_id'].append(proveedor.uom_id.id)
            if len(lista_ubicaciones['uom_id']) > 0:
                lista_productos.append((0,0,{'product_id': producto.id,'uom_id':lista_ubicaciones['uom_id'][0] ,'qty': 0,'qty_stock': producto.with_context(location = ubicacion_usuario_actual).qty_available}))
        return lista_productos

    productos_ids = fields.One2many('pedidos_tienda.producto', 'pedido_id', 'Productos')

    def generar(self):
        importe_minimo = self.env.user.company_id.po_double_validation_amount
        compras = {}
        productos = {}
        ubicacion_usuario_actual = self.env.user.default_location_id.id
        tipos_albaran = self.env['stock.picking.type'].search([('code','=','incoming'), ('default_location_dest_id','=', ubicacion_usuario_actual)])
        picking_type_id = 0
        productos_cantidad_minima = []
        for albaran in tipos_albaran:
            picking_type_id = albaran.id
        for linea in self.productos_ids:
            if linea.qty > 0:
                for producto in linea.product_id:
                    proveedores = {'partner_id':[],'uom_id':[],'cantidad_minima': 0}
                    for proveedor in producto.seller_ids:
                        for ubicacion in proveedor.location_ids:
                            if ubicacion.id == ubicacion_usuario_actual:
                                proveedores['partner_id'].append(proveedor.name.id)
                                proveedores['uom_id'].append(proveedor.uom_id.id)
                                proveedores['cantidad_minima'] = proveedor.min_qty
                                proveedores['precio'] = proveedor.price
                    llave = proveedores['partner_id'][0]
                    if llave not in compras:
                        compras[llave]= {
                            'partner_id': proveedores['partner_id'][0],
                            'productos':[{
                                'product_id':linea.product_id.id,
                                'name': linea.product_id.name,
                                'uom_id': proveedores['uom_id'][0],
                                'price': proveedores['precio'],
                                'qty': linea.qty,
                            }],
                            'monto': proveedores['precio'] * linea.qty,
                        }
                    else:
                        monto = 0
                        compras[llave]['monto'] += linea.qty * proveedores['precio']
                        compras[llave]['productos'].append({
                                'product_id':linea.product_id.id,
                                'name': linea.product_id.name,
                                'uom_id': proveedores['uom_id'][0],
                                'price': proveedores['precio'],
                                'qty': linea.qty,
                        })

        compras_monto = []
        for compra in compras.values():
            proveedor_id = self.env['res.partner'].search([('id','=',compra['partner_id'])])
            if compra['monto'] < proveedor_id.monto_minimo_compras:
                compras_monto.append('Proveedor: ' + str(proveedor_id.name) + ' Monto minimo compras: ' + str(proveedor_id.monto_minimo_compras) + ' Monto compra: ' + str(compra['monto']))

        if len(compras_monto) == 0:
            for i in compras.values():
                compra = {
                    'partner_id':i['partner_id'],
                    'picking_type_id': picking_type_id,
                }
                compra_id = self.env['purchase.order'].create(compra)
                for producto in i['productos']:
                    linea_compra = {
                        'order_id': compra_id.id,
                        'date_planned': datetime.datetime.now(),
                        'product_id': producto['product_id'],
                        'name': producto['name'],
                        'product_qty': producto['qty'],
                        'product_uom': producto['uom_id'],
                        'price_unit': producto['price'],
                    }
                    linea_id = self.env['purchase.order.line'].create(linea_compra)
                if compra_id.amount_total < importe_minimo:
                    compra_id.button_approve()
        else:
            raise UserError('Los siguientes productos no cumplen con el minimo de compra: ' +str(compras_monto))
        return True

class predidos_tienda_producto(models.TransientModel):

    _name = 'pedidos_tienda.producto'

    pedido_id = fields.Many2one('pedidos_tienda.orden_compra','Pedido', required=True)
    product_id = fields.Many2one('product.product',string='Producto')
    uom_id = fields.Many2one('product.uom','Unidad de medida',readonly=True)
    qty = fields.Integer('Cantidad')
    qty_stock = fields.Integer('Cantidad actual', readonly=True)
