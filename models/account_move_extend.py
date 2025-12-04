from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    expected_payment_date = fields.Date(
        string="Data prevista pagamento/incasso"
    )

    cashflow_category = fields.Selection(
        [
            ("customer_invoice", "Fattura Cliente"),
            ("supplier_invoice", "Fattura Fornitore"),
            ("financial", "Finanziario"),
            ("recurring", "Ricorrente"),
        ],
        string="Categoria cashflow",
    )

    is_cashflow_override = fields.Boolean(
        string="Override data cashflow"
    )
