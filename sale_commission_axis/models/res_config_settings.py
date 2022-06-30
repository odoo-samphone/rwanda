# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    commission_based = fields.Selection(
        [('commission_sale', 'Commission On Sale'), ('commission_invoice', 'Commission On Invoice'),
         ('commission_payment', 'Commission On Payment')],default="commission_sale")
    product_commission_based_on = fields.Selection(
        [("product", "Product"), ("product_category", "Product Category"), ("margin", "Margin")])
    product_commission_with_type = fields.Selection(
        [("fix", "Fix Price"), ("margin", "Margin"), ("commission_exception", "Commission Exception")])
    commission_account_id = fields.Many2one("account.account",string="Commission Account")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id, readonly=True)

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.commission_based = self.company_id.commission_based
        self.product_commission_based_on = self.company_id.product_commission_based_on
        self.product_commission_with_type = self.company_id.product_commission_with_type
        self.commission_account_id = self.company_id.commission_account_id

    def set_values(self):
        self.ensure_one()
        super(ResConfigSettings, self).set_values()
        self.company_id.commission_based = self.commission_based
        self.company_id.product_commission_based_on = self.product_commission_based_on
        self.company_id.product_commission_with_type = self.product_commission_with_type
        self.company_id.commission_account_id = self.commission_account_id