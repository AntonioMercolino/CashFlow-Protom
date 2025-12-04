{
    "name": "Protom Cashflow",
    "version": "16.0.1.0.0",
    "summary": "Modulo di gestione cashflow integrato con contabilità Odoo",
    "author": "Protom",
    "depends": [
        "account",
        "account_accountant",
        "base",
        "crm",
    ],
    "data": [
        "security/cashflow_security.xml",
        "security/ir.model.access.csv",
        # "views/cashflow_menu.xml",
        # "views/cashflow_forecast_views.xml",
        # "views/cashflow_recurring_cost_views.xml",
        "views/cashflow_loan_views.xml",
        # "views/cashflow_bank_facility_views.xml",
        # "views/cashflow_simulation_views.xml",
        # "views/cashflow_dashboard_views.xml",
        # "views/account_move_extend_views.xml",
        # "data/cashflow_cron.xml",
    ],
    # "assets": {
    #     "web.assets_backend": [
    #         "protom_cashflow/static/src/js/cashflow_dashboard.js",
    #         "protom_cashflow/static/src/xml/cashflow_dashboard_templates.xml",
    #         "protom_cashflow/static/src/css/cashflow_styles.css",
    #     ],
    # },
    "installable": True,
    "application": True,
}
