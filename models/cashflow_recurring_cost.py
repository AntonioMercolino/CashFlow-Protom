from odoo import  models, fields

class CashFlowRecurringCost(models.Model):
    _name = "cashflow.recurring.cost"
    _description = "Costo Ricorrente Cashflow"

    name = fields.Char(
        string="Nome Costo Ricorrente",
        required=True
    )

    amount = fields.Float(
        string="Importo",
        required=True
    )

    frequency = fields.Selection(
        [
            ("monthly", "Mensile"),
            ("quarterly", "Trimestrale"),
            ("semi_annually", "Semestrale"),
            ("annually", "Annuale"),
        ],
        string="Frequenza",
        required=True
    )

    next_due_date = fields.Date(
        string="Prossima Data di Scadenza",
        required=True
    )
    start_date = fields.Date(
        string="Data Inizio",
        required=True
    )
    end_date = fields.Date(
        string="Data Fine"
    )


    active = fields.Boolean(
        string="Attivo",
        default=True
    )
    category_id = fields.Many2one(
        "cashflow.category",
        string="Categoria Cashflow"
    )
    company_id = fields.Many2one(
        "res.company",
        string="Azienda",
        required=True,
        default=lambda self: self.env.company
    )   