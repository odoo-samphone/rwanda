# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, date

class WizardSaleCommission(models.TransientModel):
    _name = "wizard.sale.commission"

    start_date = fields.Date(default=date.today(),string='From Date', required=True)
    end_date = fields.Date('To Date', required=True)
    user_ids = fields.Many2many('res.users', 'commission_report_res_user_rel', 'res_user_id', 'report_commission_id',
                                string="Sales Person", copy=False)
    commission = fields.Selection([("standard","Standard Based"),("partner","Partner Based"),("product","Product/Product Category/Margin"),("discount","Discount")])
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    def print_pdf(self):
        return self.env.ref('sale_commission_axis.action_report_commission').report_action(self)

