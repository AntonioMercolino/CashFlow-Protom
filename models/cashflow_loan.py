from odoo import models, fields, api
from datetime import datetime, timedelta
import math


class CashflowLoan(models.Model):
    _name = "cashflow.loan"
    _description = "Mutuo / Leasing per Cashflow"
    _order = "start_date"

    name = fields.Char(string="Nome Prestito", required=True)

    loan_type = fields.Selection([
        ("loan", "Mutuo"),
        ("leasing", "Leasing"),
    ], string="Tipo", required=True)

    bank_id = fields.Many2one("res.bank", string="Banca", required=True)

    principal_amount = fields.Monetary(
        string="Importo Principale",
        required=True
    )

    interest_rate = fields.Float(
        string="Tasso di Interesse (%)",
        required=True,
        help="Tasso annuo nominale"
    )

    duration_months = fields.Integer(
        string="Durata (mesi)",
        required=True
    )

    start_date = fields.Date(string="Data Inizio", required=True)
    end_date = fields.Date(string="Data Fine", compute="_compute_end_date", store=True)

    installment_amount = fields.Monetary(
        string="Importo Rata",
        compute="_compute_installment_amount",
        store=True,
        help="Calcolata automaticamente in base a tasso e durata"
    )

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

    installment_ids = fields.One2many(
        "cashflow.loan.installment",
        "loan_id",
        string="Rate Generate"
    )

    state = fields.Selection([
        ("draft", "Bozza"),
        ("active", "Attivo"),
        ("closed", "Chiuso"),
    ], default="draft")

    # -------------------------------------------
    # COMPUTE FIELDS
    # -------------------------------------------

    @api.depends("start_date", "duration_months")
    def _compute_end_date(self):
        for loan in self:
            if loan.start_date and loan.duration_months:
                loan.end_date = loan.start_date + timedelta(days=loan.duration_months * 30)

    @api.depends("principal_amount", "interest_rate", "duration_months")
    def _compute_installment_amount(self):
        """
        Calcolo rata usando formula ammortamento alla francese
        R = P * (r / (1 - (1+r)^-n))
        """
        for loan in self:
            if loan.principal_amount and loan.interest_rate and loan.duration_months:
                P = loan.principal_amount
                r = (loan.interest_rate / 100) / 12
                n = loan.duration_months
                if r == 0:
                    loan.installment_amount = P / n
                else:
                    loan.installment_amount = P * (r / (1 - math.pow(1 + r, -n)))

    # -------------------------------------------
    # GENERAZIONE PIANO RATE
    # -------------------------------------------

    def generate_installment_plan(self):
        """Genera il piano rate completo"""
        self.ensure_one()

        # pulizia rate esistenti
        self.installment_ids.unlink()

        date_cursor = self.start_date
        amount = self.installment_amount

        for i in range(self.duration_months):
            self.env["cashflow.loan.installment"].create({
                "loan_id": self.id,
                "date": date_cursor,
                "amount": amount,
            })

            # avanzamento di 1 mese
            date_cursor = date_cursor + timedelta(days=30)

        self.state = "active"
        return True
    def action_generate_installments(self):
        for loan in self:
            loan.generate_installment_plan()
