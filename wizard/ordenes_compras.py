# -*- encoding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
import base64
import datetime
import logging
import dateutil.parser

class pedidos_tienda_orden_compra(models.TransientModel):
    _name = 'pedidos_tienda.orden_compra'

    def _default_productos(self):
        lista_productos = []
        ubicacion_usuario_actual = self.env.user.default_location_id.id
        domain = []
        logging.warning(self.plantilla_id.name)
        if self.plantilla_id:
            domain = [('plantilla_id', '=', self.plantilla_id.id)]
        logging.warning(domain)
        productos = self.env['product.product'].search(domain)
        logging.warning(productos)
        for producto in productos:
            lista_ubicaciones = {'uom_id':[]}
            for proveedor in producto.seller_ids:
                for ubicacion in proveedor.location_ids:
                    if ubicacion.id == ubicacion_usuario_actual:
                        lista_ubicaciones['uom_id'].append(proveedor.uom_id.id)
            if len(lista_ubicaciones['uom_id']) > 0:
                lista_productos.append((0,0,{'product_id': producto.id,'uom_id':lista_ubicaciones['uom_id'][0] ,'qty': 0,'qty_stock': producto.with_context(location = ubicacion_usuario_actual).qty_available}))
        return lista_productos

    @api.onchange('plantilla_id')
    def _onchange_plantilla(self):
        if self.plantilla_id:
            for line in self.productos_ids:
                self.productos_ids = [(3, line.id)]

            self.productos_ids = self._default_productos()

    fecha_entrega = fields.Date('Fecha de entrega')
    plantilla_id = fields.Many2one('pedidos_tienda.plantilla_producto', string='Plantilla')
    productos_ids = fields.One2many('pedidos_tienda.producto', 'pedido_id','Productos', default=_default_productos)

    def convertir(self, producto, proveedor_uom, cantidad, precio):
        res = {}

        if producto.uom_po_id.category_id.id != proveedor_uom.category_id.id:
            conversion = self.env['pedidos_tienda.conversion_uom'].search([('product_id', '=', producto.id), ('uom_id', '=', proveedor_uom.id), ('uom_dest_id', '=', producto.uom_po_id.id)])
            if not conversion:
                raise UserError('No existen conversión especial para la siguiente combinación:\n\nProducto: ' + producto.name + '\nUnidad de medida origen: ' + proveedor_uom.name + '\nUnidad de medida destino: ' + producto.uom_po_id.name)
            res['cantidad'] = cantidad * conversion[0].factor
            res['precio'] = precio / conversion[0].factor
        else:
            res['cantidad'] = cantidad
            res['precio'] = precio

        return res

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
                                proveedores['partner_id'].append(proveedor.partner_id.id)
                                proveedores['uom_id'].append(proveedor.uom_id.id)
                                proveedores['cantidad_minima'] = proveedor.min_qty
                                proveedores['precio'] = proveedor.price

                    llave = proveedores['partner_id'][0]
                    proveedor_uom_id = self.env['uom.uom'].search([('id', '=', proveedores['uom_id'][0])])
                    conv = self.convertir(linea.product_id, proveedor_uom_id, linea.qty, proveedores['precio'])

                    if conv['cantidad'] == linea.qty:
                        uom_linea = proveedores['uom_id'][0]
                    else:
                        uom_linea = linea.product_id.uom_po_id.id

                    if llave not in compras:
                        compras[llave]= {
                            'partner_id': proveedores['partner_id'][0],
                            'productos':[{
                                'product_id':linea.product_id.id,
                                'name': linea.product_id.name,
                                'uom_id': uom_linea,
                                'qty': conv['cantidad'],
                                'ref_uom_id': proveedores['uom_id'][0],
                                'ref_qty': linea.qty,
                                'price': conv['precio'],
                            }],
                            'monto': proveedores['precio'] * linea.qty,
                        }
                    else:
                        monto = 0
                        compras[llave]['monto'] += linea.qty * proveedores['precio']
                        compras[llave]['productos'].append({
                                'product_id':linea.product_id.id,
                                'name': linea.product_id.name,
                                'uom_id': uom_linea,
                                'qty': conv['cantidad'],
                                'ref_uom_id': proveedores['uom_id'][0],
                                'ref_qty': linea.qty,
                                'price': conv['precio'],
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
                    'user_id': self.env.user.id,
                }
                compra_id = self.env['purchase.order'].create(compra)
                for producto in i['productos']:
                    linea_compra = {
                        'order_id': compra_id.id,
                        'date_planned': datetime.datetime.now(),
                        'product_id': producto['product_id'],
                        'name': producto['name'],
                        'product_uom': producto['uom_id'],
                        'product_qty': producto['qty'],
                        'ref_product_uom': producto['ref_uom_id'],
                        'ref_product_qty': producto['ref_qty'],
                        'price_unit': producto['price'],
                    }
                    linea_id = self.env['purchase.order.line'].create(linea_compra)
                    linea_id._compute_tax_id()

                if self.env.user.company_id.po_double_validation == 'one_step' or (self.env.user.company_id.po_double_validation == 'two_step' and compra_id.amount_total < importe_minimo):
                    compra_id.button_approve()

                compra_id.date_planned = self.fecha_entrega

        else:
            raise UserError('Los siguientes productos no cumplen con el minimo de compra: ' +str(compras_monto))
        return True

class predidos_tienda_producto(models.TransientModel):

    _name = 'pedidos_tienda.producto'

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = []
        if self.product_id:
            ubicacion_usuario_actual = self.env.user.default_location_id.id
            lista_ubicaciones = {'uom_id':[]}
            for proveedor in self. product_id.seller_ids:
                for ubicacion in proveedor.location_ids:
                    if ubicacion.id == ubicacion_usuario_actual:
                        lista_ubicaciones['uom_id'].append(proveedor.uom_id.id)
            if len(lista_ubicaciones['uom_id']) > 0:
                self.uom_id = lista_ubicaciones['uom_id'][0]
                self.qty_stock = self.product_id.with_context(location = ubicacion_usuario_actual).qty_available
        return res

    @api.model
    def _get_domain_product(self):
        productos = []
        productos_ids = self.env['product.product'].search([('purchase_ok', '=', True)])
        if productos_ids:
            for producto in productos_ids:
                for proveedor in producto.seller_ids:
                    for ubicacion in proveedor.location_ids:
                        if ubicacion == self.env.user.default_location_id:
                            productos.append(producto.id)
        return [('purchase_ok', '=', True),('id','in',productos)]

    pedido_id = fields.Many2one('pedidos_tienda.orden_compra','Pedido', required=True)
    product_id = fields.Many2one('product.product',string='Producto',domain=_get_domain_product)
    uom_id = fields.Many2one('uom.uom','Unidad de medida',readonly=True)
    qty = fields.Integer('Cantidad')
    qty_stock = fields.Integer('Cantidad actual', readonly=True)
