from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_scale = fields.Boolean(string="Has Scale", default=False)
    scale_value = fields.Float(string="Scale", digits=(10, 2))

class ProductProduct(models.Model):
    _inherit = 'product.product'

    scale_value = fields.Float(related='product_tmpl_id.scale_value', readonly=True)
    has_scale = fields.Boolean(related='product_tmpl_id.has_scale', readonly=True)