from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = "account.payment"

    planned_date = fields.Date(
        string="Data prevista pagamento/incasso"
    )
    cashflow_inclusion = fields.Boolean(
        string="Includi nel cashflow",
        default=True,
        help="Se deselezionato, questo pagamento non verrà considerato nel calcolo del cashflow.",
    )
    

