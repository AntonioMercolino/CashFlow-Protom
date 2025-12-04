from odoo import models, fields, api

class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    forecast_line_id = fields.Many2one(
        "cashflow.forecast.line",
        string="Linea Forecast Cashflow",
        help="Movimento previsionale collegato a questo movimento bancario."
    )

    cashflow_reconciled = fields.Boolean(
        string="Riconciliato Cashflow",
        default=False,
        help="Indica che il movimento bancario è stato allineato con la previsione cashflow."
    )

    @api.model
    def match_with_cashflow_forecast(self):
        """
        Abbina automaticamente movimenti bancari a linee di forecast,
        in base a amount + partner e data vicina.
        """
        forecast_obj = self.env["cashflow.forecast.line"]

        for line in self:
            if line.cashflow_reconciled:
                continue  

            tolerance_days = 5

            domain = [
                ("amount", "=", line.amount),
                ("partner_id", "=", line.partner_id.id),
                ("is_simulation", "=", False),
                ("date", ">=", line.date - fields.Date.to_date(str(tolerance_days))),
                ("date", "<=", line.date + fields.Date.to_date(str(tolerance_days))),
            ]

            forecast = forecast_obj.search(domain, limit=1)

            if forecast:
                line.forecast_line_id = forecast.id
                line.cashflow_reconciled = True

                # opzionale: marcare anche forecast
                forecast.is_realized = True if hasattr(forecast, "is_realized") else None

        return True

