from odoo import models, fields, api
from datetime import timedelta
from dateutil.relativedelta import relativedelta  # normalmente presente in Odoo


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
            ("move", "Fattura/Nota"),
            ("payment", "Pagamento"),
            ("bank_statement", "Movimento Bancario"),
            ("recurring", "Ricorrente"),
            ("loan", "Prestito"),
            ("simulation", "Simulazione")
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
    bank_account_id = fields.Many2one(
        'account.journal', 
        string='Conto Bancario', 
        domain=[('type', '=', 'bank')]
    )
    bank_id = fields.Many2one(
        'res.bank', 
        string='Banca', 
        related='bank_account_id.bank_id', # Campo calcolato o correlato
        store=True # Importante per l'aggregazione veloce nel Pivot!
    )
    cashflow_category = fields.Many2one(
        'cashflow.category', # Modello custom da creare (es. 'Affitti', 'Crediti V/Clienti', 'Mutui')
        string='Categoria Cashflow',
        required=True 
    )
    # =========================================================
    #  MOTORE PRINCIPALE DI FORECAST
    # =========================================================

    @api.model
    def compute_forecast(
        self,
        date_from=False,
        date_to=False,
        company_id=False,
        reset_existing=True,
    ):
        """
        Calcola il forecast di cashflow per un intervallo di date.

        - Cancella le linee NON di simulazione (is_simulation = False) nel range indicato
        - Genera nuove linee da:
            * Fatture clienti da incassare (inflow)
            * Fatture fornitori da pagare (outflow)
            * Pagamenti con planned_date (in/out)
            * Costi ricorrenti (outflow)
            * Rate mutui/leasing (outflow)

        CONVENZIONE IMPORTI:
            * Entrata  (inflow)  => amount > 0
            * Uscita   (outflow) => amount < 0
        """

        # -----------------------------------------------------
        # 1) Normalizzazione parametri
        # -----------------------------------------------------
        if not company_id:
            company = self.env.company
        else:
            company = self.env["res.company"].browse(company_id)

        if not date_from:
            date_from = fields.Date.context_today(self)
        if not date_to:
            # default: orizzonte 90 giorni
            date_to = date_from + timedelta(days=90)

        # sicurezza: cast a date (nel caso arrivino stringhe)
        if isinstance(date_from, str):
            date_from = fields.Date.from_string(date_from)
        if isinstance(date_to, str):
            date_to = fields.Date.from_string(date_to)

        # -----------------------------------------------------
        # 2) Pulizia forecast esistente (non simulazioni)
        # -----------------------------------------------------
        if reset_existing:
            existing_domain = [
                ("is_simulation", "=", False),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
            ]
            # opzionale: filtra per company se aggiungi campo company_id in futuro
            self.search(existing_domain).unlink()

        lines_to_create = []

        # Helper per business unit: se i modelli hanno business_unit_id lo usiamo,
        # altrimenti lo lasciamo vuoto.
        def _get_bu(record):
            return getattr(record, "business_unit_id", False).id if hasattr(record, "business_unit_id") else False

        # =====================================================
        # 3) FATTURE CLIENTI/FORNITORI (account.move)
        # =====================================================

        Move = self.env["account.move"]

        # Fatture clienti da incassare (outstanding)
        customer_invoices = Move.search([
            ("company_id", "=", company.id),
            ("state", "=", "posted"),
            ("move_type", "in", ["out_invoice", "out_refund"]),
            ("payment_state", "in", ["not_paid", "partial"]),
        ])

        for inv in customer_invoices:
            # data di riferimento: expected_payment_date se override, altrimenti scadenza
            pay_date = inv.expected_payment_date or inv.invoice_date_due
            if not pay_date:
                continue
            if pay_date < date_from or pay_date > date_to:
                continue

            amount = inv.amount_residual  # residuo da incassare
            if inv.move_type == "out_refund":
                # una nota di credito riduce un incasso => trattiamola come uscita o riduzione flusso
                amount = -abs(amount)

            if not amount:
                continue

            line_vals = {
                "name": inv.name or inv.ref or "Fattura cliente",
                "date": pay_date,
                "amount": amount if amount >= 0 else amount,  # inflow positivo, eventuali casi particolari rimangono
                "partner_id": inv.partner_id.id,
                "is_simulation": False,
                "type": "inflow" if amount >= 0 else "outflow",
                "source_model": "move",
                "source_id": inv.id,
                "business_unit_id": _get_bu(inv),
            }
            lines_to_create.append(line_vals)

        # Fatture fornitori da pagare
        supplier_invoices = Move.search([
            ("company_id", "=", company.id),
            ("state", "=", "posted"),
            ("move_type", "in", ["in_invoice", "in_refund"]),
            ("payment_state", "in", ["not_paid", "partial"]),
        ])

        for inv in supplier_invoices:
            pay_date = inv.expected_payment_date or inv.invoice_date_due
            if not pay_date:
                continue
            if pay_date < date_from or pay_date > date_to:
                continue

            amount = inv.amount_residual
            # convenzione: uscite sempre negative
            if inv.move_type == "in_invoice":
                amount = -abs(amount)    # fattura fornitore = uscita
            else:
                amount = abs(amount)     # nota di credito fornitore = "entrata" (rimborso)

            if not amount:
                continue

            line_vals = {
                "name": inv.name or inv.ref or "Fattura fornitore",
                "date": pay_date,
                "amount": amount,
                "partner_id": inv.partner_id.id,
                "is_simulation": False,
                "type": "inflow" if amount > 0 else "outflow",
                "source_model": "move",
                "source_id": inv.id,
                "business_unit_id": _get_bu(inv),
            }
            lines_to_create.append(line_vals)

        # =====================================================
        # 4) PAGAMENTI (account.payment)
        # =====================================================

        Payment = self.env["account.payment"]

        payments = Payment.search([
            ("company_id", "=", company.id),
            ("state", "in", ["posted", "sent"]),
            ("cashflow_inclusion", "=", True),
        ])

        for pay in payments:
            pay_date = pay.planned_date or pay.date
            if not pay_date:
                continue
            if pay_date < date_from or pay_date > date_to:
                continue

            amount = pay.amount or 0.0
            if not amount:
                continue

            # inbound = incasso, outbound = pagamento
            if pay.payment_type == "inbound":
                signed_amount = abs(amount)
                flow_type = "inflow"
            elif pay.payment_type == "outbound":
                signed_amount = -abs(amount)
                flow_type = "outflow"
            else:
                # trasferimenti tra conti: opzionale includerli o meno.
                # Per ora li ignoriamo.
                continue

            line_vals = {
                "name": pay.ref or pay.name or "Pagamento",
                "date": pay_date,
                "amount": signed_amount,
                "partner_id": pay.partner_id.id,
                "is_simulation": False,
                "type": flow_type,
                "source_model": "payment",
                "source_id": pay.id,
                "business_unit_id": _get_bu(pay),
            }
            lines_to_create.append(line_vals)

        # =====================================================
        # 5) COSTI RICORRENTI (cashflow.recurring.cost)
        # =====================================================

        Recurring = self.env["cashflow.recurring.cost"]

        recurring_costs = Recurring.search([
            ("company_id", "=", company.id),
            ("active", "=", True),
        ])

        for cost in recurring_costs:
            # generiamo tutte le occorrenze entro il periodo date_from/date_to
            current_date = cost.next_due_date or cost.start_date
            if not current_date:
                continue

            # se l'intervallo richiesto è oltre la fine del contratto, saltiamo
            end_date = cost.end_date or date_to

            # portiamo current_date almeno a date_from
            while current_date and current_date < date_from:
                current_date = _next_recurring_date(current_date, cost.frequency)
                if current_date and current_date > end_date:
                    break

            while current_date and current_date <= date_to and current_date <= end_date:
                amount = -abs(cost.amount or 0.0)  # costo = uscita negativa

                if amount:
                    line_vals = {
                        "name": cost.name,
                        "date": current_date,
                        "amount": amount,
                        "partner_id": False,
                        "is_simulation": False,
                        "type": "outflow",
                        "source_model": "recurring",
                        "source_id": cost.id,
                        "business_unit_id": _get_bu(cost),
                    }
                    lines_to_create.append(line_vals)

                # prossima scadenza
                current_date = _next_recurring_date(current_date, cost.frequency)
                if not current_date or current_date > end_date:
                    break

        # =====================================================
        # 6) RATE MUTUI / LEASING (cashflow.loan.installment)
        # =====================================================

        LoanInstallment = self.env["cashflow.loan.installment"]

        installments = LoanInstallment.search([
            ("company_id", "=", company.id),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
        ])

        for inst in installments:
            loan = inst.loan_id
            if not loan:
                continue

            amount = -abs(inst.amount or 0.0)  # rata = uscita

            line_vals = {
                "name": f"Rata {loan.name}",
                "date": inst.date,
                "amount": amount,
                "partner_id": loan.bank_id and loan.bank_id.partner_id.id or False,
                "is_simulation": False,
                "type": "outflow",
                "source_model": "loan",
                "source_id": inst.id,
                "business_unit_id": _get_bu(loan),
            }
            lines_to_create.append(line_vals)

        # =====================================================
        # 7) Creazione in batch delle linee
        # =====================================================

        if lines_to_create:
            self.create(lines_to_create)

        return True


# ---------------------------------------------------------
# Helper di modulo (fuori dalla classe)
# ---------------------------------------------------------

def _next_recurring_date(current_date, frequency):
    """Calcola la prossima data per un costo ricorrente.

    frequency: 'monthly', 'quarterly', 'semi_annually', 'annually'
    """
    if not current_date:
        return False

    if frequency == "monthly":
        return current_date + relativedelta(months=1)
    elif frequency == "quarterly":
        return current_date + relativedelta(months=3)
    elif frequency == "semi_annually":
        return current_date + relativedelta(months=6)
    elif frequency == "annually":
        return current_date + relativedelta(years=1)
    else:
        # fallback: un mese
        return current_date + relativedelta(months=1)
