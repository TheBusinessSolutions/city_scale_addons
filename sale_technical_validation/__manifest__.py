{
    'name': 'Sale Technical Validation',
    'version': '18.0.2.0.0',
    'category': 'Sales/Sales',
    'summary': 'Native technical validation workflow with configurable checklist and scale management.',
    'depends': ['sale', 'product'], # REMOVED smile_checklist
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_checklist_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}