/** @odoo-module **/

import PaymentScreen from 'point_of_sale.PaymentScreen';
import { patch } from 'web.utils';
var rpc = require('web.rpc');

patch(PaymentScreen.prototype, 'pos_customizations_payment_screen', {

        async validateOrder(isForceValidate) {
            if(this.env.pos.config.cash_rounding) {
                if(!this.env.pos.get_order().check_paymentlines_rounding()) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Rounding error in payment lines'),
                        body: this.env._t("The amount of your payment lines must be rounded to validate the transaction."),
                    });
                    return;
                }
            }
            if (await this._isOrderValid(isForceValidate)) {
                // remove pending payments before finalizing the validation
                for (let line of this.paymentLines) {
                    if (!line.is_done()) this.currentOrder.remove_paymentline(line);
                }
                await this._finalizeValidation();
            }
            debugger;
            rpc.query({
                model: 'pos.order',
                method: 'set_pos_reference',
                args: [this.env.pos.validated_orders_name_server_id_map[this.env.pos.get_order().name],
                        document.getElementById('ref_number').value],
            });
        }
});