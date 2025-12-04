
# Cashflow Module for Odoo

Modulo custom per la gestione avanzata del Cashflow in Odoo, con funzionalità di forecast, simulazioni, mutui/leasing, costi ricorrenti, castelletti bancari e riconciliazione automatica con movimenti bancari reali.

Questo modulo è progettato per fornire una visione completa della liquidità aziendale presente e futura, integrandosi con i moduli contabili standard di Odoo.

---

## 📌 Struttura del modulo

```
cashflow/
│
├── models/
│   ├── account_bank_statement_line.py
│   ├── account_move_extend.py
│   ├── account_payment_extend.py
│   ├── cashflow_bank_facility.py
│   ├── cashflow_forecast_line.py
│   ├── cashflow_loan.py
│   ├── cashflow_loan_installment.py
│   ├── cashflow_recurring_cost.py
│   └── __init__.py
│
├── views/
│   ├── cashflow_loan_views.xml
│   ├── cashflow_loan_installment_views.xml
│   └── __init__.py
│
├── security/
│   ├── ir.model.access.csv
│   └── cashflow_security.xml
│
├── data/
│   └── cashflow_cron.xml
│
├── static/
│   └── src/ (widget dashboard OWL - to be implemented)
│
├── README.md
└── __manifest__.py
```

---

## 🧱 Modelli Creati

### `cashflow.forecast.line`
Rappresenta una *riga di previsione* (entrata/uscita futura).  
È il modello centrale per il calcolo del cashflow.

**Campi principali:**
- `date`
- `type`
- `amount`
- `source_model`
- `source_id`
- `partner_id`
- `business_unit_id`
- `is_simulation`
- `is_realized`
- `bank_statement_line_id`

---

### `cashflow.loan`
Gestione Mutui / Leasing aziendali.  

**Caratteristiche:**
- Calcolo automatico delle rate  
- Generazione del piano rate  
- Integrazione nel forecast  

**Campi principali:**
- `name`
- `loan_type`
- `bank_id`
- `principal_amount`
- `interest_rate`
- `duration_months`
- `installment_amount`
- `start_date`
- `end_date`
- `installment_ids`

---

### `cashflow.loan.installment`
Rappresenta una singola rata del mutuo/leasing.

**Campi:**
- `loan_id`
- `date`
- `amount`

---

### `cashflow.recurring.cost`
Gestione costi ricorrenti (stipendi, affitti, canoni).

---

### `cashflow.bank.facility`
Gestione castelletti bancari.

---

## 🧱 Modelli Estesi

### `account.move`
Campi aggiunti:
- `expected_payment_date`
- `cashflow_category`
- `is_cashflow_override`
- `bank_facility_id`

### `account.payment`
Campi aggiunti:
- `planned_date`
- `cashflow_inclusion`

### `account.bank.statement.line`
Campi aggiunti:
- `forecast_line_id`
- `cashflow_reconciled`

---

## 👁️‍🗨️ Viste Generate

### Mutui/Leasing
- Tree view
- Form view
- Bottone: Genera Piano Rate

### Rate
- Tree view
- Form view

---

## 🔐 Sicurezza

### Gruppi:
- `Cashflow User`
- `Cashflow Manager`
- `Cashflow Admin`

### ACL:
- definito in `ir.model.access.csv`

---

## ⚙️ Funzionalità Implementate

- Gestione mutui e generazione automatica rate
- Gestione costi ricorrenti
- Gestione castelletti bancari
- Forecast line dei movimenti previsti
- Riconciliazione forecast ↔ movimenti bancari
- Cron automatico match cashflow
- Wizard per riconciliazione avanzata

---

## 🧭 Funzionalità Future (TODO)

- Dashboard Cashflow (OWL)
- Forecast engine completo
- Simulazioni avanzate
- Analisi scostamenti
- Integrazione CRM previsionale
- Notifiche e alert

---

## 🔌 Dipendenze

```
"depends": [
    "base",
    "account",
    "account_accountant",
    "crm",
    "web"
]
```

---

## 🚀 Installazione

1. Copiare la cartella `cashflow` in `/odoo/custom/addons/`
2. Aggiornare elenco moduli:
```
odoo-bin -u cashflow -d <database>
```
3. Accedere al menu Cashflow dopo l'installazione.

---

## 👨‍💻 Autore

Progetto Cashflow Odoo  
Sviluppato da: **Antonio Mercolino**
