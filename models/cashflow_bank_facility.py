from odoo import  models, fields

class CashflowBankFacility(models.Model):
    _name = "cashflow.bank.facility"
    _description = "Linea di Credito per Cashflow"
    _order = "start_date"

    name = fields.Char(string="Nome Linea di Credito", required=True)

    bank_id = fields.Many2one("res.bank", string="Banca", required=True)

    credit_limit = fields.Monetary(
        string="Limite di Credito",
        required=True
    )

    interest_rate = fields.Float(
        string="Tasso di Interesse (%)",
        required=True,
        help="Tasso annuo nominale"
    )

    start_date = fields.Date(string="Data Inizio", required=True)
    end_date = fields.Date(string="Data Fine", required=True)

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    company_id = fields.Many2one(
        "res.company",
        string="Azienda",
        required=True,
        default=lambda self: self.env.company
    )