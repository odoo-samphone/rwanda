# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

class ResPartner(models.Model):
	_inherit = "res.partner"

	affiliated = fields.Boolean(string="Is Affiliate")