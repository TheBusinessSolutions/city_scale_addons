from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_scale = fields.Boolean(string="Has Scale", default=False)
    scale_value = fields.Float(string="Scale", digits=(10, 2))