# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import calendar as cal


class SalesCommission(models.Model):
	_name = "sale.commission"
	_description = "Sales Commission"

	name = fields.Char(string="Commission Name")
	user_ids = fields.Many2many('res.users', 'commission_res_user_rel', 'res_user_id', 'commission_id', string="Sales Person", copy=False)
	commission_type = fields.Selection([("standard","Standard Based"),("partner","Partner Based"),("product","Product/Product Category/Margin"),("discount","Discount")],required=1)
	affiliated_commi = fields.Float(string="Affiliate Partner Based Commission (%)")
	non_affiliated_commi = fields.Float(string="Non-Affiliate Partner Based Commission (%)")
	standard_commi = fields.Float(string="Standard Commission (%)")
	type_ids = fields.One2many(
        'commission.type', 'commission_id', string='Sales Commission Exception')
	no_discount_commission = fields.Float(string="No Discount Commission")
	max_discount = fields.Float(string="Max Discount (%)")
	discount_commi = fields.Float(string="Discount > 25 (%) Commission (%) ")
	rule_ids = fields.One2many('commission.rules', 'commission_id', string="Commission Rules")

	@api.onchange('commission_type')
	def _onchange_commission(self):
		commission_id = self.env["sale.commission"].search([])
		for commission in commission_id:
			if commission.commission_type == self.commission_type:
				raise UserError(_('Already create a commission for %s.(%) Based')%commission.commission_type)

	@api.constrains('type_ids')
	def _check_exist_product_in_line(self):
		for commission in self:
			exist_product_list = []
			exist_product_categ_list = []
			exist_with_type_list = []
			exist_based_on_list = []
			for line in commission.type_ids:
				if line.product_id.id in exist_product_list and line.with_type in exist_with_type_list and line.based_on in exist_based_on_list:
					raise ValidationError(_('Product should be one per line.%s Type,%s Based on %s Product')%(line.with_type,line.based_on,line.product_id.name))
				if line.product_categ_id.id in exist_product_categ_list and line.with_type in exist_with_type_list and line.based_on in exist_based_on_list:
					raise ValidationError(_('Product Category should be one per line.%s Type,%s Based on %s Product Category')%(line.with_type,line.based_on,line.product_categ_id.name))
				if line.product_id:
					exist_product_list.append(line.product_id.id)
					exist_product_categ_list.append(line.product_id.id)
					exist_with_type_list.append(line.with_type)

	@api.constrains('rule_ids')
	def _check_discount(self):
		for commission in self:
			discount_lst =[]
			for commission_line in commission.rule_ids:
				if commission_line.discount < commission.max_discount:
					raise ValidationError(_("Discount must be greater than %s Discount")%commission.max_discount)
				if commission_line.discount in discount_lst:
					raise ValidationError(_("Already Exist Discount %s (%)")%commission_line.discount)
				discount_lst.append(commission_line.discount)

class CommissionRules(models.Model):
	_name = "commission.rules"
	_description = "Commission Rules"

	discount = fields.Float(string="Discount")
	commission = fields.Float(string="Commission")
	commission_id = fields.Many2one("sale.commission",string="Commission Type")

class CommissionType(models.Model):
	_name = "commission.type"
	_description = "Commission Type"

	based_on = fields.Selection([("product","Product"),("product_category","Product Categpry"),("margin","Margin")],default="product")
	with_type = fields.Selection([("fix","Fix Price"),("margin","Margin"),("commission_exception","Commission Exception")],default="fix")
	commission_id = fields.Many2one("sale.commission")
	product_id = fields.Many2one('product.product',string="Product")
	product_categ_id = fields.Many2one('product.category',string="Product Category")
	target_price = fields.Float(string="Target Price")
	above_price_commi = fields.Float(string="Above Price Commission (%)")
	target_margin = fields.Float("Target Margin (%)")
	above_margin_commi = fields.Float("Above Margin Commission (%)")
	below_margin_commi = fields.Float("Below Margin Commission (%)")
	commi_exception = fields.Float("Commissiomn (%)")

class commissionLineData(models.Model):
	_name = "commission.line.data"
	_description = "Commission Line Data"

	date = fields.Date(string="Date")
	description = fields.Text(string="Description")
	user_id = fields.Many2one('res.users',string="SalesPerson")
	amount = fields.Float(string="Amount")
	order_id = fields.Many2one("sale.order",string="Order")
	product_id = fields.Many2one("product.product",string="Product")
	product_categ_id = fields.Many2one("product.category",string="Product")
	invoice_id = fields.Many2one("account.move",string="Invoice")
	payment_id = fields.Many2one("account.payment",string="Payment")
	commission_type = fields.Char(String="Commission Type")

	@api.model
	def get_count_list(self):
		total_sale_commission = self.env['commission.line.data'].sudo().search_count([("order_id","!=",False)])
		total_inv_commission = self.env['commission.line.data'].sudo().search_count([("invoice_id","!=",False),("payment_id","=",False)])
		total_payment_commission = self.env['commission.line.data'].sudo().search_count([("payment_id","!=",False)])
		return {
			'total_sale_commission': total_sale_commission,
			'total_inv_commission': total_inv_commission,
			'total_payment_commission': total_payment_commission,
		}

	@api.model
	def get_week_commission(self):
		cr = self._cr

		query = """
	       SELECT cld.date AS date_time,count(*) as count
	       FROM commission_line_data cld 
	       group by cld.date
	       order by cld.date
	       """
		cr.execute(query)
		partner_data = cr.dictfetchall()
		data_set = {}
		list_value = []
		dict = {}
		days = ["Monday", "Tuesday", "Wednesday", "Thursday",
				"Friday", "Saturday", "Sunday"]
		for data in partner_data:
			if data['date_time']:
				mydate = data['date_time'].weekday()
				if mydate >= 0:
					value = days[mydate]
					list_value.append(value)
					list_value1 = list(set(list_value))
					for record in list_value1:
						count = 0
						for rec in list_value:
							if rec == record:
								count = count + 1
							dict.update({record: data['count']})
						keys, values = zip(*dict.items())
						data_set.update({"data": dict})
		return data_set

	@api.model
	def get_monthly_commission(self):
		cr = self._cr

		query = """
	       SELECT cld.date AS start_date,count(*) as count
	       FROM commission_line_data cld
	       group by cld.date
	       order by cld.date
	       """
		cr.execute(query)
		partner_data = cr.dictfetchall()
		data_set = {}
		list_value = []
		dict = {}
		months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
				  'August', 'September', 'October', 'November', 'December']

		for data in partner_data:
			if data['start_date']:
				mydate = data['start_date'].month
				for month_idx in range(0, 13):
					if mydate == month_idx:
						value = cal.month_name[month_idx]
						list_value.append(value)
						list_value1 = list(set(list_value))
						for record in list_value1:
							count = 0
							for rec in list_value:
								if rec == record:
									count = count + 1
								dict.update({record: count})
						keys, values = zip(*dict.items())
						data_set.update({"data": dict})
		return data_set

	@api.model
	def get_commission_data(self):
		cr = self._cr
		query = """
	        SELECT cld.date AS date_start,count(*) as count,cld.order_id as order_id,sum(amount) as total_amount
	       FROM commission_line_data cld
	       group by cld.order_id,date
	       order by cld.date
		"""
		cr.execute(query)
		category_data = cr.dictfetchall()
		a_key = "count"
		amount = 0.0
		for data_total in category_data:
			amount += data_total["total_amount"]
		values_of_category = [a_dict[a_key] for a_dict in category_data]
		data_set = {}
		data_set.update({
			'Category': values_of_category,
		})
		return data_set

	@api.model
	def get_sale_commission_pie(self):
		cr = self._cr
		query = """
			SELECT count(*) as count,cld.order_id as order_nm,sum(amount) as total_amount,
			so.name as order_nm
			FROM commission_line_data cld join  sale_order so on so.id =cld.order_id
			group by cld.order_id,so.name
			order by cld.order_id
		"""
		cr.execute(query)
		payroll_data = cr.dictfetchall()
		payroll_label = []
		payroll_dataset = []
		data_set = {}
		for data in payroll_data:
			payroll_label.append(data['order_nm'])
			payroll_dataset.append(data['total_amount'])
		data_set.update({"payroll_dataset": payroll_dataset})
		data_set.update({"payroll_label": payroll_label})
		return data_set

	@api.model
	def get_invoice_commission_pie(self):
		cr = self._cr
		query = """SELECT count(*) as count,cld.invoice_id as invoice_nm,sum(amount) as total_amount,ai.name as invoice_nm
				FROM commission_line_data cld join  account_move ai on ai.id =cld.invoice_id
				group by cld.invoice_id,ai.name
				order by cld.invoice_id
			"""
		cr.execute(query)
		payroll_data = cr.dictfetchall()
		payroll_label = []
		payroll_dataset = []
		data_set = {}
		for data in payroll_data:
			payroll_label.append(data['invoice_nm'])
			payroll_dataset.append(data['total_amount'])
		data_set.update({"payroll_dataset": payroll_dataset})
		data_set.update({"payroll_label": payroll_label})
		return data_set

	@api.model
	def get_payment_commission_pie(self):
		cr = self._cr
		query = """
					SELECT count(*) as count,cld.payment_id as payment_nm,cld.amount as total_amount,
					ap.move_id as payment_nm
					FROM commission_line_data cld join  account_payment ap on ap.id =cld.payment_id
					group by cld.payment_id,ap.move_id,cld.amount
					order by cld.payment_id
				"""
		cr.execute(query)
		payroll_data = cr.dictfetchall()
		payroll_label = []
		payroll_dataset = []
		data_set = {}
		for data in payroll_data:
			payroll_label.append(data['payment_nm'])
			payroll_dataset.append(data['total_amount'])
		data_set.update({"payroll_dataset": payroll_dataset})
		data_set.update({"payroll_label": payroll_label})
		return data_set