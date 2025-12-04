from odoo import models, fields

class CashflowForecastLine(models.Model):
    _name = "cashflow.forecast.line"
    _description = "Linea di Forecast Cashflow"

    name = fields.Char(
        string="Descrizione",
        required=True
    )
    date = fields.Date(
        string="Data Previsione",
        required=True
    )
    amount = fields.Float(
        string="Importo",
        required=True
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner"
    )
    is_simulation = fields.Boolean(
        string="Simulazione",
        default=False,
        help="Indica se questa linea è una simulazione e non un dato reale."
    )
    type = fields.Selection(
        [
            ("inflow", "Entrata"),
            ("outflow", "Uscita"),
        ],
        string="Tipo",
        required=True
    )
    source_model = fields.Selection(
        [
            ("move","Fattura/Nota"), 
            ("payment","Pagamento"), 
            ("bank_statement","Movimento Bancario"),
            ("recurring","Ricorrente"),
            ("loan","Prestito"),
            ("simulation","Simulazione")
        ],
        string="Modello Sorgente",
        help="Modello Odoo da cui proviene questa linea di forecast."
    )
    source_id = fields.Integer(
        string="ID Sorgente",
        help="ID del record sorgente nel modello specificato."
    )
    business_unit_id = fields.Many2one(
        "res.business.unit",
        string="Unità di Business",
        help="Unità di business associata a questa linea di forecast."
    )