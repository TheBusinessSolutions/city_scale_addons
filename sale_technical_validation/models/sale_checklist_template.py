from odoo import api, fields, models

class SaleChecklistTemplate(models.Model):
    _name = 'sale.checklist.template'
    _description = 'Sales Checklist Template'
    _order = 'name'

    name = fields.Char(string='Checklist Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    line_ids = fields.One2many('sale.checklist.template.line', 'template_id', string='Checklist Items')

class SaleChecklistTemplateLine(models.Model):
    _name = 'sale.checklist.template.line'
    _description = 'Checklist Template Line'
    _order = 'sequence'

    template_id = fields.Many2one('sale.checklist.template', required=True, ondelete='cascade')
    name = fields.Char(string='Task', required=True, translate=True)
    sequence = fields.Integer(default=10)
    is_mandatory = fields.Boolean(string='Mandatory', default=False)