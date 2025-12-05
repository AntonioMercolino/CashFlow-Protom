from odoo import models, fields

class CashflowCategory(models.Model):
    _name = 'cashflow.category'
    _description = 'Cashflow Category'

    name = fields.Char(string='Category Name', required=True)
    code = fields.Char(string='Category Code', required=True)
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'The Category Code must be unique!'),
    ]