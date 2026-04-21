from . import models
from odoo import exceptions, _

def pre_init_check(cr):
    """Check if a checklist already exists for sale.order"""
    cr.execute("""
        SELECT id FROM checklist 
        WHERE model_id = (SELECT id FROM ir_model WHERE model = 'sale.order')
        LIMIT 1
    """)
    if cr.fetchone():
        raise exceptions.UserError(_(
            "A checklist already exists for Sales Orders.\n\n"
            "This module requires exclusive use of the Checklist feature for sale.order.\n"
            "Please either:\n"
            "1. Delete the existing checklist for sale.order, OR\n"
            "2. Migrate its tasks to this module's 'Technical Validation' checklist.\n\n"
            "Go to: Settings > Technical > Checklists"
        ))