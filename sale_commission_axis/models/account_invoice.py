# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import  UserError

class AccountInvoice(models.Model):
    _inherit = "account.move"

    @api.onchange('partner_id')
    def commission_type(self):
        res = {}
        config_id = self.env["res.config.settings"].search([], limit=1, order='id desc')
        last_id = config_id and max(config_id)
        if last_id.commission_based == "commission_invoice" or last_id.commission_based == "commission_payment":
            self.config_inv_commission = True
        user_ids = self.env["res.users"].search([('id', '=', self.env.user.id)])
        commission_ids = self.env["sale.commission"].search([("user_ids", "in", user_ids.id)])
        commission_lst = []
        for commission in commission_ids:
            commission_lst.append(commission.id)
        res['domain'] = {'sale_commission_inv': [('id', 'in', commission_lst)]}
        return res

    commission_inv_line_ids = fields.One2many("commission.line.data", 'invoice_id', string="Sale Commission")
    inv_commission_bool = fields.Boolean()
    pay_commission_bool = fields.Boolean()
    sale_commission_inv = fields.Many2one("sale.commission")
    config_inv_commission = fields.Boolean()

    def action_post(self):
        res = super(AccountInvoice, self).action_post()
        config_ids = self.env['res.config.settings'].search([], order='id desc')
        last_id = config_ids and max(config_ids)
        commission_id = self.env['sale.commission'].search([("id", '=', self.sale_commission_inv.id)])

        if last_id.commission_based == "commission_invoice":
            if self.id:
                self.inv_commission_bool = True
                for line_id in self.invoice_line_ids:
                    if not line_id.tax_ids:
                        if commission_id.commission_type == "standard":
                            commission_line_data = self.env["commission.line.data"].create({"date": self.invoice_date,
                                                                                            "user_id": self.user_id.id,
                                                                                            "description": commission_id.name + " " + line_id.product_id.name,
                                                                                            "amount": ((
                                                                                                               commission_id.standard_commi * line_id.price_subtotal) / 100),
                                                                                            "invoice_id": self.id,
                                                                                            "product_id": line_id.product_id.id,
                                                                                            "commission_type":commission_id.commission_type,
                                                                                            })
                        elif commission_id.commission_type == "partner":
                            if self.partner_id.affiliated:
                                afilliate_per = commission_id.affiliated_commi
                            else:
                                afilliate_per = commission_id.non_affiliated_commi
                            commission_line_data = self.env["commission.line.data"].create({"date": self.invoice_date,
                                                                                            "user_id": self.user_id.id,
                                                                                            "description": commission_id.name + " " + line_id.product_id.name,
                                                                                            "amount": ((
                                                                                                               afilliate_per * line_id.price_subtotal) / 100),
                                                                                            "invoice_id": self.id,
                                                                                            "product_id": line_id.product_id.id,
                                                                                            "commission_type": commission_id.commission_type,
                                                                                            })
                        elif commission_id.commission_type == "product":
                            commission_line_data = self.env["commission.line.data"].create({"date": self.invoice_date,
                                                                                            "user_id": self.user_id.id,
                                                                                            "description": commission_id.name + " " + line_id.product_id.name,
                                                                                            "invoice_id": self.id,
                                                                                            "commission_type": commission_id.commission_type,
                                                                                            })
                            if last_id.product_commission_based_on == 'product' and last_id.product_commission_with_type == 'fix':
                                commi_prod_fix = self.env['commission.type'].search(
                                    [("product_id", "=", line_id.product_id.id), ("based_on", "=", "product"),
                                     ("with_type", "=", "fix")], limit=1)
                                if commi_prod_fix and commi_prod_fix.target_price < line_id.price_subtotal:
                                    commission_line_data.update(
                                        {"amount": ((commi_prod_fix.above_price_commi * line_id.price_subtotal) / 100),
                                         "product_id": line_id.product_id.id,
                                         })
                            elif last_id.product_commission_based_on == 'product_category' and last_id.product_commission_with_type == 'fix':
                                commi_prod_categ_fix = self.env['commission.type'].search(
                                    [("product_categ_id", "=", line_id.product_id.categ_id.id),
                                     ("based_on", "=", "product_category"),
                                     ("with_type", "=", "fix")], limit=1)
                                if commi_prod_categ_fix and commi_prod_categ_fix.target_price < line_id.price_subtotal:
                                    commission_line_data.update(
                                        {"amount": ((
                                                            commi_prod_categ_fix.above_price_commi * line_id.price_subtotal) / 100),
                                         "product_categ_id": line_id.product_id.categ_id.id,
                                         })
                            elif last_id.product_commission_based_on == 'margin' and last_id.product_commission_with_type == 'fix':
                                commi_margin_fix = self.env['commission.type'].search(
                                    [("with_type", "=", "fix"), ("based_on", "=", "margin")], limit=1)
                                if commi_margin_fix and commi_margin_fix.target_price < line_id.price_subtotal:
                                    commission_line_data.update(
                                        {"amount": ((
                                                                commi_margin_fix.above_price_commi * line_id.price_subtotal) / 100),
                                         })
                            elif last_id.product_commission_based_on == 'product' and last_id.product_commission_with_type == 'commission_exception':
                                commi_prod_commi_excep = self.env['commission.type'].search(
                                    [("product_id", "=", line_id.product_id.id), ("based_on", "=", "product"),
                                     ("with_type", "=", "commission_exception")], limit=1)
                                if commi_prod_commi_excep:
                                    commission_line_data.update(
                                        {"amount": ((
                                                            commi_prod_commi_excep.commi_exception * line_id.price_subtotal) / 100),
                                         "product_id": line_id.product_id.id,
                                         })
                            elif last_id.product_commission_based_on == 'product_category' and last_id.product_commission_with_type == 'commission_exception':
                                commi_prod_categ_commi_excep = self.env['commission.type'].search(
                                    [("product_categ_id", "=", line_id.product_id.categ_id.id),
                                     ("based_on", "=", "product_category"),
                                     ("with_type", "=", "commission_exception")], limit=1)
                                if commi_prod_categ_commi_excep:
                                    commission_line_data.update(
                                        {"amount": ((
                                                            commi_prod_categ_commi_excep.commi_exception * line_id.price_subtotal) / 100),
                                         "product_categ_id": line_id.product_id.categ_id.id,
                                         })
                            elif last_id.product_commission_based_on == 'margin' and last_id.product_commission_with_type == 'commission_exception':
                                commi_margin_commi_excep = self.env['commission.type'].search(
                                    [("based_on", "=", "margin"), ("with_type", "=", "commission_exception")], limit=1)
                                if commi_margin_commi_excep:
                                    commission_line_data.update(
                                        {"amount": ((
                                                            commi_margin_commi_excep.commi_exception * line_id.price_subtotal) / 100),
                                         })
                            elif last_id.product_commission_based_on == 'product' and last_id.product_commission_with_type == 'margin':
                                commi_prod_margin = self.env['commission.type'].search(
                                    [("product_id", "=", line_id.product_id.id), ("based_on", "=", "product"),
                                     ("with_type", "=", "margin")], limit=1)
                                product_diff_price = ((
                                                              line_id.product_id.lst_price - line_id.product_id.standard_price) * line_id.quantity)
                                margin_price = commi_prod_margin.target_margin * 100
                                if commi_prod_margin and margin_price > product_diff_price:
                                    amount = ((line_id.price_subtotal * commi_prod_margin.below_margin_commi) / 100)
                                else:
                                    amount = ((line_id.price_subtotal * commi_prod_margin.above_margin_commi) / 100)
                                commission_line_data.update(
                                    {"amount": amount,
                                     "product_id": line_id.product_id.id,
                                     })
                            elif last_id.product_commission_based_on == 'product_category' and last_id.product_commission_with_type == 'margin':
                                commi_prod_categ_margin = self.env['commission.type'].search(
                                    [("product_categ_id", "=", line_id.product_id.categ_id.id),
                                     ("based_on", "=", "product_category"),
                                     ("with_type", "=", "margin")], limit=1)
                                product_diff_price = ((
                                                              line_id.product_id.lst_price - line_id.product_id.standard_price) * line_id.quantity)
                                margin_price = commi_prod_categ_margin.target_margin * 100
                                if commi_prod_categ_margin and margin_price > product_diff_price:
                                    amount = ((
                                                          line_id.price_subtotal * commi_prod_categ_margin.below_margin_commi) / 100)
                                else:
                                    amount = ((
                                                          line_id.price_subtotal * commi_prod_categ_margin.above_margin_commi) / 100)
                                commission_line_data.update(
                                    {"amount": amount,
                                     "product_categ_id": line_id.product_id.categ_id.id,
                                     })
                            elif last_id.product_commission_based_on == 'margin' and last_id.product_commission_with_type == 'margin':
                                commi_margin_margin = self.env['commission.type'].search(
                                    [("with_type", "=", "margin"), ("based_on", "=", "margin")], limit=1)
                                product_diff_price = ((
                                                              line_id.product_id.lst_price - line_id.product_id.standard_price) * line_id.quantity)
                                margin_price = commi_margin_margin.target_margin * 100
                                if commi_margin_margin and margin_price > product_diff_price:
                                    amount = ((line_id.price_subtotal * commi_margin_margin.below_margin_commi) / 100)
                                else:
                                    amount = ((line_id.price_subtotal * commi_margin_margin.above_margin_commi) / 100)
                                commission_line_data.update(
                                    {"amount": amount,
                                     })
                        elif commission_id.commission_type == "discount":
                            if line_id.discount:
                                for commission_rule in commission_id.rule_ids:
                                    if commission_rule.discount == line_id.discount:
                                        disc_amt = ((commission_rule.commission * line_id.price_subtotal) / 100)
                                    else:
                                        raise UserError(
                                            _('No Commission rule for  %s.discount ') % line_id.discount)
                            else:
                                disc_amt = ((line_id.price_subtotal * commission_id.no_discount_commission) / 100)
                            commission_line_data = self.env["commission.line.data"].create({"date": self.invoice_date,
                                                                                            "user_id": self.user_id.id,
                                                                                            "description": commission_id.name + " " + line_id.product_id.name,
                                                                                            "amount": disc_amt,
                                                                                            "invoice_id": self.id,
                                                                                            "product_id": line_id.product_id.id,
                                                                                            "commission_type": commission_id.commission_type,
                                                                                            })
        return res

class PaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"

    def create_invoices(self):
        res = super(PaymentInv, self).create_invoices()
        invoice_id = self.env["account.move"].search([("id",'=',res['res_id'])])
        for invoice in invoice_id:
            config_id = self.env["res.config.settings"].search([], limit=1, order='id desc')
            last_id = config_id and max(config_id)
            if last_id.commission_based == "commission_invoice" or last_id.commission_based == "commission_payment":
                invoice.config_inv_commission = True
            order_id = self.env['sale.order'].search([("name","=",invoice.name)])
            invoice.update({'sale_commission_inv':order_id.sale_commission})
        user_ids = self.env["res.users"].search([('id', '=', self.env.user.id)])
        commission_ids = self.env["sale.commission"].search([("user_ids", "in", user_ids.id)])
        commission_lst = []
        for commission in commission_ids:
            commission_lst.append(commission.id)
        res['domain'] = {'sale_commission_inv': [('id', 'in', commission_lst)]}
        return res
