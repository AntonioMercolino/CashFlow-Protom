{
    "name": "Protom Cashflow",
    "version": "1.0.0",
    "summary": "Modulo di gestione cashflow integrato con contabilità Odoo",
    "author": "Protom",
    "depends": [
        "account",
        "account_accountant",
        "base",
        "crm",
        "web",
    ],
    "data": [
        "security/cashflow_security.xml",
        "security/ir.model.access.csv",
        "views/cashflow_menu.xml",
        "views/cashflow_loan_installment_views.xml",
        "views/cashflow_loan_views.xml",
        "views/cashflow_category_views.xml",
        "views/cashflow_forecast_line_views.xml",
        "wizard/cashflow_dashboard_wizard_views.xml",
    ],
    # "assets": {
    #     "web.assets_backend": [
    #         "cashflow/static/src/css/cashflow_dashboard.css",
    #         "cashflow/static/src/js/cashflow_dashboard_qweb.js",
    #         "cashflow/static/src/xml/cashflow_dashboard_template.xml",
    #     ],
    # },
    "installable": True,
    "application": True,
}
