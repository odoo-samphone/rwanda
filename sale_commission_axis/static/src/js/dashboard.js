odoo.define('sale_commission_axis.MyCustomAction',  function (require) {
"use strict";
var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var rpc = require('web.rpc');
var register_view = require('web.view_registry');
var Widget = require('web.Widget');
var ajax = require('web.ajax');
var session = require('web.session');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var MyCustomAction = AbstractAction.extend({
    template: 'DashboardView',
    cssLibs: [
        '/sale_commission_axis/static/src/css/nv.d3.css'
    ],
    jsLibs: [
        '/sale_commission_axis/static/src/js/Chart.js',
    ],
    events: {
          'click .total_sale_commission': 'action_total_sale_commission',
          'click .total_inv_commission': 'action_total_inv_commission',
          'click .total_payment_commission': 'action_total_payment_commission',
          'click #stock_moves': 'render_stock_moves',
          'click #color_filter8': 'render_stock_moves',
    },

    init: function(parent, context) {
        this._super(parent, context);
        var self = this;
    },

    start: function() {
        var self = this;
        self.render_dashboards();
        self.render_graphs();
        return this._super();
    },
    reload: function () {
            window.location.href = this.href;
    },
    render_dashboards: function(value) {
        var self = this;
        var sales_commission_dashboard = QWeb.render('DashboardView', {
            widget: self,
        });
        rpc.query({
                model: 'commission.line.data',
                method: 'get_count_list',
                args: []
            })
            .then(function (result){
             console.log(">>>>>>>>>>>>>",result['total_sale_commission'])
                    self.$el.find('.total-sale-commission').text(result['total_sale_commission'])
                    self.$el.find('.total-inv-commission').text(result['total_inv_commission'])
                    self.$el.find('.total-payment-commission').text(result['total_payment_commission'])
            });


        return sales_commission_dashboard
    },
      action_total_sale_commission:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Total Sale Commission"),
            type: 'ir.actions.act_window',
            res_model:'commission.line.data',
            view_mode: 'list,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['order_id','!=',false]],
            target: 'current'
        },)
    },
      action_total_inv_commission:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Total Invoice Commission"),
            type: 'ir.actions.act_window',
            res_model:'commission.line.data',
            view_mode: 'list,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['invoice_id','!=',false],['payment_id','=',false]],
            target: 'current'
        },)
    },
      action_total_payment_commission:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Total Payment Commission"),
            type: 'ir.actions.act_window',
            res_model:'commission.line.data',
            view_mode: 'list,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['payment_id','!=',false]],
            target: 'current'
        },)
    },
      getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },

      render_graphs: function(){
        var self = this;
        self.weekly_commission();
        self.monthly_commission();
        self.render_sale_commission_pie();
        self.render_invoice_commission_pie();
        self.render_payment_commission_pie();
    },

      weekly_commission: function() {
        var self = this;
        var ctx = this.$el.find('#weekcommission')
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        rpc.query({
                model: 'commission.line.data',
                method: 'get_week_commission',

            })
            .then(function (result) {
                var data = result.data;
                var day = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]
                var week_data = [];
                if (data){
                    for(var i = 0; i < day.length; i++){
                        day[i] == data[day[i]]
                        var day_data = day[i];
                        var day_count = data[day[i]];
                        if(!day_count){
                                day_count = 0;
                        }
                        week_data[i] = day_count

                    }
                }
                var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: day ,
                    datasets: [{
                        label: ' Commission',
                        data: week_data,
                        backgroundColor: bg_color_list,
                        borderColor: bg_color_list,
                        borderWidth: 1,
                        pointBorderColor: 'white',
                        pointBackgroundColor: 'red',
                        pointRadius: 5,
                        pointHoverRadius: 10,
                        pointHitRadius: 30,
                        pointBorderWidth: 2,
                        pointStyle: 'rectRounded'
                    }]
                },
                options: {
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                                max: Math.max.apply(null,week_data),
                              }
                        }]
                    },
                    responsive: true,
                    maintainAspectRatio: true,
                    leged: {
                        display: true,
                        labels: {
                            fontColor: 'black'
                        }
                },
            },
        });

            });
    },
      monthly_commission: function() {
        var self = this;
        var ctx = this.$el.find('#monthlycommission')
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        rpc.query({
                model: 'commission.line.data',
                method: 'get_monthly_commission',
            })
            .then(function (result) {
                var data = result.data
                var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                                'August', 'September', 'October', 'November', 'December']
                var month_data = [];

                if (data){
                    for(var i = 0; i < months.length; i++){
                        months[i] == data[months[i]]
                        var day_data = months[i];
                        var month_count = data[months[i]];
                        if(!month_count){
                                month_count = 0;
                        }
                        month_data[i] = month_count

                    }
                }
                var myChart = new Chart(ctx, {
                type: 'bar',
                data: {

                    labels: months,
                    datasets: [{
                        label: ' Commission',
                        data: month_data,
                        backgroundColor: bg_color_list,
                        borderColor: bg_color_list,
                        borderWidth: 1,
                        pointBorderColor: 'white',
                        pointBackgroundColor: 'red',
                        pointRadius: 1,
                        pointHoverRadius: 10,
                        pointHitRadius: 30,
                        pointBorderWidth: 1,
                        pointStyle: 'rectRounded'
                    }]
                },
                options: {
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                                max: Math.max.apply(null,month_data),
                              }
                        }]
                    },
                    responsive: true,
                    maintainAspectRatio: true,
                    leged: {
                        display: true,
                        labels: {
                            fontColor: 'black'
                        }
                    },
                },
            });
        });
    },
    render_sale_commission_pie: function() {
        var self = this;
        var session_allowed_company_ids = session.user_context.allowed_company_ids || [];
        var piectx = this.$el.find('#sale_commission_data')
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        rpc.query({
                model: 'commission.line.data',
                method: 'get_sale_commission_pie',
            })
            .then(function (result) {
                    bg_color_list = []
                    for (var i=0;i<=result.payroll_dataset.length;i++){
                        bg_color_list.push(self.getRandomColor())
                    }
                    var pieChart = new Chart(piectx,{
                        type: 'pie',
                        data: {
                            datasets: [{
                                data: result.payroll_dataset,
                                backgroundColor: bg_color_list,
                                label: 'Sales Commission Pie'
                            }],
                            labels:result.payroll_label,
                        },
                        options: {
                            responsive: true
                        }
                    });
            });
            },
    render_invoice_commission_pie: function() {
        var self = this;
        var session_allowed_company_ids = session.user_context.allowed_company_ids || [];
        var piectx = this.$el.find('#invoice_commission_data')
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        rpc.query({
                model: 'commission.line.data',
                method: 'get_invoice_commission_pie',
            })
            .then(function (result) {
                    bg_color_list = []
                    for (var i=0;i<=result.payroll_dataset.length;i++){
                        bg_color_list.push(self.getRandomColor())
                    }
                    var pieChart = new Chart(piectx,{
                        type: 'pie',
                        data: {
                            datasets: [{
                                data: result.payroll_dataset,
                                backgroundColor: bg_color_list,
                                domain: [['invoice_id','!=',false],['payment_id','=',false]],
                                label: 'Invoice Commission Pie'
                            }],
                            labels:result.payroll_label,
                        },
                        options: {
                            responsive: true
                        }
                    });
            });
            },
    render_payment_commission_pie: function() {
        var self = this;
        var session_allowed_company_ids = session.user_context.allowed_company_ids || [];
        var piectx = this.$el.find('#payment_commission_data')
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        rpc.query({
                model: 'commission.line.data',
                method: 'get_payment_commission_pie',
            })
            .then(function (result) {
                    bg_color_list = []
                    for (var i=0;i<=result.payroll_dataset.length;i++){
                        bg_color_list.push(self.getRandomColor())
                    }
                    var pieChart = new Chart(piectx,{
                        type: 'pie',
                        data: {
                            datasets: [{
                                data: result.payroll_dataset,
                                backgroundColor: bg_color_list,
                                label: 'Payment Commission Pie'
                            }],
                            labels:result.payroll_label,
                        },
                        options: {
                            responsive: true
                        }
                    });
            });
            },
});
core.action_registry.add("sales_commission_dashboard", MyCustomAction);
//core.action_registry.add("Helpdesk_dashboard", MyCustomAction);

return MyCustomAction;
});