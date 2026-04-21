from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[
        ('waiting_scale', 'Waiting Scale'),
        ('waiting_pricing', 'Waiting Pricing')
    ], ondelete={'waiting_scale': 'set draft', 'waiting_pricing': 'set draft'})

    is_technical_verified = fields.Boolean(
        string="Technically Verified", 
        compute='_compute_is_technical_verified', 
        store=True
    )

    @api.depends('order_line.product_id.product_tmpl_id.scale_value', 'x_checklist_progress_rate')
    def _compute_is_technical_verified(self):
        for order in self:
            # Check if at least one product in the order has a scale value
            has_scale_data = any(line.product_id.product_tmpl_id.scale_value for line in order.order_line)
            # Check if checklist has any progress (at least one item checked)
            # Note: x_checklist_progress_rate is added by the smile_checklist module
            has_checklist_progress = order.x_checklist_progress_rate > 0
            order.is_technical_verified = has_scale_data and has_checklist_progress

    def action_send_to_scale(self):
        """Changes state to Waiting Scale"""
        self.write({'state': 'waiting_scale'})
        # TODO: Add notification logic in Phase 3
        return True