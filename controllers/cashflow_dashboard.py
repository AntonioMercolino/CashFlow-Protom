from odoo import http, fields
from odoo.http import request
from datetime import timedelta


class CashflowDashboardController(http.Controller):

    @http.route("/cashflow/dashboard/kpi", type="json", auth="user")
    def get_kpi(self, date_from=None, date_to=None, company_id=None):
        
        # 1) Normalizzazione date
        today = fields.Date.today()
        date_from = fields.Date.from_string(date_from) if date_from else today
        date_to = fields.Date.from_string(date_to) if date_to else today + timedelta(days=90)

        Forecast = request.env["cashflow.forecast.line"].sudo()

        domain = [
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("is_simulation", "=", False),
        ]

        if company_id:
            # Se aggiungerai company_id nel forecast, filtra qui
            domain.append(("company_id", "=", int(company_id)))

        lines = Forecast.search(domain, order="date asc")

        # -----------------------------------------------------
        # 2) KPI PRINCIPALI
        # -----------------------------------------------------
        income = sum(lines.filtered(lambda l: l.type == "inflow").mapped("amount"))
        outcome = abs(sum(lines.filtered(lambda l: l.type == "outflow").mapped("amount")))
        balance = income - outcome

        # -----------------------------------------------------
        # 3) COSTRUZIONE SERIE TEMPORALE PER GRAFICO SALDO
        # -----------------------------------------------------
        daily_balance = []
        cumulative_balance = 0

        current_date = date_from
        while current_date <= date_to:
            day_lines = lines.filtered(lambda l, d=current_date: l.date == d)

            daily_in = sum(day_lines.filtered(lambda l: l.type == "inflow").mapped("amount"))
            daily_out = sum(day_lines.filtered(lambda l: l.type == "outflow").mapped("amount"))

            cumulative_balance += (daily_in + daily_out)

            daily_balance.append({
                "date": str(current_date),
                "inflow": daily_in,
                "outflow": abs(daily_out),
                "cumulative": cumulative_balance,
            })

            current_date += timedelta(days=1)

        # -----------------------------------------------------
        # 4) RISPOSTA JSON PER LA DASHBOARD
        # -----------------------------------------------------
        return {
            "kpi": {
                "income": income,
                "outcome": outcome,
                "balance": balance,
            },
            "chart": {
                "daily": daily_balance,
            },
            "meta": {
                "date_from": str(date_from),
                "date_to": str(date_to),
            }
        }
