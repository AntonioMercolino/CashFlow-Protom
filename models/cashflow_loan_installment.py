from odoo import models, fields


class CashflowLoanInstallment(models.Model):
    _name = "cashflow.loan.installment"
    _description = "Rata Prestito / Leasing"
    _order = "date"

    loan_id = fields.Many2one(
        "cashflow.loan",
        string="Prestito",
        required=True,
        ondelete="cascade"
    )

    date = fields.Date(
        string="Data Rata",
        required=True
    )

    amount = fields.Monetary(
        string="Importo Rata",
        required=True
    )

    currency_id = fields.Many2one(
        related="loan_id.currency_id",
        readonly=True
    )

    company_id = fields.Many2one(
        related="loan_id.company_id",
        readonly=True
    )
