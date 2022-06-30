#-*- coding:utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import  UserError

class SaleOrderReport(models.AbstractModel):
    _name = 'report.sale_commission_axis.report_commissionsummary'

    def get_data(self,data):
        data_dict = {}
        final_list = []
        lst = []
        if data.start_date > data.end_date:
            raise UserError(_("End date should be greater than start date."))
        else:
            for user in data.user_ids:
                lst.append(user.id)
            commission_sql = """SELECT cld.date as date, cld.user_id as salesperson, 
                                    cld.commission_type as commission_type,
                                    cld.order_id as order_id, cld.invoice_id as invoice_id,
                                    cld.payment_id as payment_id,
                                    cld.amount as amount FROM commission_line_data as cld
                                            WHERE cld.date >= '%s' 
                                            AND cld.date <= '%s' 
                                            AND cld.commission_type = '%s' 
                                            AND (cld.user_id in %s) 
                                        """ % (data.start_date,data.end_date,
                                               data.commission, " (%s) " % ','.join(map(str, lst)),)
            self._cr.execute(commission_sql)
            commission_data = self._cr.dictfetchall()
            amount = 0.0
            if not commission_data:
                raise UserError(_('No Record Found'))
            else:
                for commission_line in commission_data:
                    order_id = self.env['sale.order'].browse(commission_line['order_id'])
                    invoice_id = self.env['account.move'].browse(commission_line['invoice_id'])
                    payment_id = self.env['account.payment'].browse(commission_line['payment_id'])
                    res_user_id = self.env['res.users'].browse(commission_line['salesperson'])
                    amount += commission_line['amount']
                    data_dict = {
                        "date": commission_line['date'],
                        "salesperson": res_user_id.name,
                        "commission": commission_line['commission_type'].title(),
                        "order_id": order_id.name,
                        "invoice_id": invoice_id.name,
                        "payment_id": payment_id.name,
                        'amount': commission_line['amount'],
                    }
                    final_list.append(data_dict)
            return final_list

    @api.model
    def _get_report_values(self, docids, data=None):
        sale_commission_id = self.env['wizard.sale.commission'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'wizard.sale.commission',
            'docs': sale_commission_id,
            'data': data,
            'get_data': self.get_data(sale_commission_id),
        }