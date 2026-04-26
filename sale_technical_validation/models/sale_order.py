from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Workflow States
    state = fields.Selection(selection_add=[
        ('waiting_scale', 'Waiting Scale'),
        ('waiting_pricing', 'Waiting Pricing')
    ], ondelete={'waiting_scale': 'set draft', 'waiting_pricing': 'set draft'})

    # Native Checklist Fields
    checklist_template_id = fields.Many2one('sale.checklist.template', string='Checklist Template')
    checklist_line_ids = fields.One2many('sale.order.checklist.line', 'order_id', string='Validation Tasks')
    checklist_progress_rate = fields.Float('Progress %', compute='_compute_checklist_progress', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.checklist_template_id:
                record._populate_checklist_lines()
        return records

    def write(self, vals):
        result = super().write(vals)
        if 'checklist_template_id' in vals:
            for record in self:
                record._populate_checklist_lines()
        return result

    def _populate_checklist_lines(self):
        """Populates checklist lines from the selected template."""
        self.ensure_one()
        if not self.checklist_template_id:
            self.checklist_line_ids = [(5, 0, 0)]
            return

        # Clear existing lines
        self.checklist_line_ids = [(5, 0, 0)]
        
        # Prepare new lines
        new_lines = []
        for line in self.checklist_template_id.line_ids:
            if line.name and str(line.name).strip():
                new_lines.append((0, 0, {
                    'name': str(line.name).strip(),
                    'is_mandatory': line.is_mandatory,
                    'sequence': line.sequence,
                    'is_completed': False,
                }))
        
        # Assign new lines
        if new_lines:
            self.checklist_line_ids = new_lines

    @api.depends('checklist_line_ids.is_completed')
    def _compute_checklist_progress(self):
        for order in self:
            lines = order.checklist_line_ids
            if lines:
                completed = len(lines.filtered(lambda l: l.is_completed))
                order.checklist_progress_rate = round((completed / len(lines)) * 100.0, 2)
            else:
                order.checklist_progress_rate = 0.0

    def action_send_to_scale(self):
        self.write({'state': 'waiting_scale'})
        return True

    def action_verify_data(self):
        for order in self:
            has_scale = any(line.product_id.product_tmpl_id.scale_value for line in order.order_line)
            if not has_scale:
                raise UserError(_("Please define 'Scale' value for all products in the quotation."))
            order.message_post(body=_("Technical Data Verified by %s") % self.env.user.name)
        return True

    def action_send_for_pricing(self):
        for order in self:
            has_scale = any(line.product_id.product_tmpl_id.scale_value for line in order.order_line)
            if not has_scale:
                raise UserError(_("Please define 'Scale' value for all products before sending for pricing."))
            
            mandatory_incomplete = order.checklist_line_ids.filtered(lambda l: l.is_mandatory and not l.is_completed)
            if mandatory_incomplete:
                raise UserError(_("Please complete all mandatory checklist items:\n%s") % 
                                ', '.join(mandatory_incomplete.mapped('name')))
            
            order.write({'state': 'waiting_pricing'})
            order.message_post(body=_("Sent for Pricing by %s") % self.env.user.name)
        return True
    
    def action_complete_pricing(self):
        """Technical Office: Finalizes pricing and sends back to Sales for confirmation."""
        for order in self:
            # 1. Optional: Recompute prices if pricelist changed
            # order.action_update_prices() 
            
            # 2. Change state to 'sent' so Sales User can review and Confirm
            order.write({'state': 'sent'})
            
            # 3. Notify Sales User
            order.message_post(body=_("Pricing Completed by %s. Please review and Confirm.") % self.env.user.name)
        return True

class SaleOrderChecklistLine(models.Model):
    _name = 'sale.order.checklist.line'
    _description = 'Sale Order Checklist Line'
    _order = 'sequence'

    order_id = fields.Many2one('sale.order', required=True, ondelete='cascade')
    # REMOVED required=True to prevent creation errors. Enforced in view/logic instead.
    name = fields.Char(string='Task') 
    is_completed = fields.Boolean(string='Completed', default=False)
    is_mandatory = fields.Boolean(string='Mandatory', default=False)
    sequence = fields.Integer(default=10)

    @api.constrains('name')
    def _check_name(self):
        for line in self:
            if not line.name or not str(line.name).strip():
                raise ValidationError(_("Checklist Task Name cannot be empty."))