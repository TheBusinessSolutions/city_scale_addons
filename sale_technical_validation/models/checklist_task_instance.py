from odoo import api, fields, models

class ChecklistTaskInstance(models.Model):
    _inherit = 'checklist.task.instance'

    # Add a manual checkbox
    is_manually_completed = fields.Boolean(string="Manually Completed", default=False)

    @api.depends('is_manually_completed', 'task_id.complete_domain', 'res_id')
    def _compute_complete(self):
        for inst in self:
            # If manually checked, it's complete
            if inst.is_manually_completed:
                inst.complete = True
            else:
                # Otherwise, use the original domain logic
                record = inst.env[inst.task_id.model].browse(inst.res_id)
                inst.complete = bool(record.filtered_domain(
                    safe_eval(inst.task_id.complete_domain) if inst.task_id.complete_domain else []
                ))