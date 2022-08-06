from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'pos.order'

    pos_reference = fields.Char('POS Reference')

    @api.model
    def set_pos_reference(self, sale_id, reference):
        sale_order = self.search([('id', '=', sale_id)])
        sale_order.write({'pos_reference': reference})

    @api.model
    def check_serial_lot(self, product_id, lot_number):
        lot_id = self.env['stock.production.lot'].search([('product_id', '=', product_id)]).filtered(
            lambda l: l.name == lot_number)
        if lot_id:
            return True
        return False
