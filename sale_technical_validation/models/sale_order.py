from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[
        ('waiting_scale', 'Waiting Scale'),
        ('waiting_pricing', 'Waiting Pricing')
    ], ondelete={'waiting_scale': 'set draft', 'waiting_pricing': 'set draft'})

    is_technical_verified = fields.Boolean(
        string="Technically Verified", 
        compute='_compute_is_technical_verified', 
        store=True,
        help="Checked when Scale data is present and Checklist items are manually verified."
    )

    @api.depends('order_line.product_id.product_tmpl_id.scale_value', 'x_checklist_progress_rate')
    def _compute_is_technical_verified(self):
        for order in self:
            # 1. Check if at least one product has scale data
            has_scale_data = any(line.product_id.product_tmpl_id.scale_value for line in order.order_line)
            
            # 2. Check if checklist progress is 100% (All items marked complete by domain)
            # Note: Since we linked complete_domain to is_technical_verified, this creates a loop.
            # To break the loop, we will rely on a manual flag or a simpler check for the button visibility.
            # For now, let's just check if Scale exists. The Checklist completion will be triggered BY this field.
            order.is_technical_verified = has_scale_data

    def action_send_to_scale(self):
        """Sales User: Moves SO to Waiting Scale"""
        self.write({'state': 'waiting_scale'})
        return True

    def action_verify_data(self):
        """Technical Office: Verifies Scale and Marks Checklist as Done"""
        for order in self:
            # 1. Validate Scale Data
            has_scale = any(line.product_id.product_tmpl_id.scale_value for line in order.order_line)
            if not has_scale:
                raise UserError(_("Please define 'Scale' value for all products in this quotation."))
            
            # 2. Set the field that triggers Checklist Completion
            # Because our Checklist Tasks have complete_domain [('is_technical_verified', '=', True)],
            # setting this field to True will automatically mark the tasks as 'Complete' in the Smile module.
            order.is_technical_verified = True
            
            # 3. Optional: Add a chatter message
            order.message_post(body=_("Technical Data Verified by %s") % self.env.user.name)

        return True

    def action_send_for_pricing(self):
        """Technical Office: Moves SO to Waiting Pricing"""
        for order in self:
            if not order.is_technical_verified:
                raise UserError(_("Please verify technical data first."))
            
            # Check if Checklist is actually 100% (Safety check)
            if order.x_checklist_progress_rate < 100.0:
                raise UserError(_("Please ensure all mandatory checklist items are completed."))

            order.write({'state': 'waiting_pricing'})
            # TODO: Trigger Product Validation here in Phase 3
            order.message_post(body=_("Sent for Pricing by %s") % self.env.user.name)
        return True