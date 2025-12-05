from odoo import  models, fields

class CashflowSimulation(models.Model):
    _name = "cashflow.simulation"
    _description = "Simulazione di Cashflow"
    _order = "name"

    name = fields.Char(string="Nome Simulazione", required=True)

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
    created_by = fields.Many2one(
        "res.users",
        string="Creato da",
        default=lambda self: self.env.user,
        required=True
    )
    status = fields.Selection([
        ("draft", "Bozza"),
        ("running", "In Esecuzione"),
        ("completed", "Completato"),
        ("cancelled", "Annullato"),
    ], string="Stato", default="draft", required=True)
    description = fields.Text(string="Descrizione")
    line_ids = fields.One2many(
        "cashflow.forecast.line",
        "is_simulation",
        string="Linee di Simulazione"
    )

    def action_start_simulation(self):
        self.status = "running"
        return True
    def action_complete_simulation(self):
        self.status = "completed"
        return True
    def action_cancel_simulation(self):
        self.status = "cancelled"
        return True
    def action_reset_simulation(self):
        self.status = "draft"
        return True
    def duplicazione_dello_scenario_reale(self):
        nuovo_scenario = self.copy({
            'name': f"{self.name} - Copia",
            'status': 'draft',
        })
        for linea in self.line_ids:
            nuovo_scenario.line_ids.create({
                'name': linea.name,
                'date': linea.date,
                'amount': linea.amount,
                'partner_id': linea.partner_id.id,
                'is_simulation': True,
                'type': linea.type,
                'source_model': linea.source_model,
                'source_id': linea.source_id,
                'business_unit_id': linea.business_unit_id.id,
            })
        return nuovo_scenario
    def spostamento_date(self, giorni):
        for linea in self.line_ids:
            nuova_data = linea.date + odoo.fields.Date.timedelta(days=giorni)
            linea.date = nuova_data
        return True
    def aggiunta_nuove_spese(self, descrizione, importo, data):
        self.line_ids.create({
            'name': descrizione,
            'date': data,
            'amount': -abs(importo),
            'is_simulation': True,
            'type': 'outflow',
        })
        return True
    def calcolo_differenziale_rispetto_al_reale(self, scenario_reale):
        differenziale = 0.0
        for linea in self.line_ids:
            linea_reale = scenario_reale.line_ids.filtered(
                lambda l: l.date == linea.date and l.name == linea.name and l.type == linea.type
            )
            if linea_reale:
                differenziale += linea.amount - linea_reale.amount
            else:
                differenziale += linea.amount
        return differenziale