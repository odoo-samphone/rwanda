# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    commission_based = fields.Selection(
        [('commission_sale', 'Commission On Sale'), ('commission_invoice', 'Commission On Invoice'),
         ('commission_payment', 'Commission On Payment')],default="commission_sale")
    product_commission_based_on = fields.Selection(
        [("product", "Product"), ("product_category", "Product Category"), ("margin", "Margin")],default="product")
    product_commission_with_type = fields.Selection(
        [("fix", "Fix Price"), ("margin", "Margin"), ("commission_exception", "Commission Exception")],default="fix")
    commission_account_id = fields.Many2one("account.account",string="Commission Account")
