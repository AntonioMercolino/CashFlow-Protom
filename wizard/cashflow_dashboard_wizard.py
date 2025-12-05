from odoo import fields, models, _
from odoo.exceptions import UserError

class CashflowDashboardWizard(models.TransientModel):
    _name = 'cashflow.dashboard.wizard'
    _description = 'Parametri Dashboard Cashflow'

    # Campi filtro
    date_from = fields.Date(string='Data Inizio', required=True)
    date_to = fields.Date(string='Data Fine', required=True)
    
    # Abbiamo visto che hai implementato bank_id su forecast.line. Usiamolo qui!
    bank_ids = fields.Many2many('res.bank', string='Banche da Includere')
    
    # Campo per filtrare tra Simulazione e Reale
    include_simulation = fields.Boolean(string='Includi Simulazioni', default=False)

    def action_open_dashboard(self):
        """
        Restituisce l'azione Act Window che apre le viste Pivot/Graph,
        applicando i filtri scelti nel Wizard.
        """
        self.ensure_one()
        
        if self.date_from > self.date_to:
            raise UserError(_("La data di inizio non può essere successiva alla data di fine."))

        # 1. Costruzione del Domain (Filtro)
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        
        if not self.include_simulation:
            # Esclude le righe marcate come simulazione
            domain.append(('is_simulation', '=', False))

        if self.bank_ids:
            # Filtro specifico per le banche selezionate
            domain.append(('bank_id', 'in', self.bank_ids.ids))

        # 2. Restituzione dell'Azione (Act Window)
        return {
            'name': 'Previsione Cashflow (Analisi)',
            'type': 'ir.actions.act_window',
            'res_model': 'cashflow.forecast.line',
            # Visualizza prima il Grafico, poi la Pivot, poi la Tree
            'view_mode': 'graph,pivot,tree',
            'domain': domain,
            'target': 'current',
        }