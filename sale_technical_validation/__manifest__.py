{
    'name': 'Sale Technical Validation',
    'version': '18.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Manage technical validation, scale data, and specialized workflow for Sales Orders.',
    'description': """
        This module adds a technical validation workflow to Sales Orders:
        - New states: Waiting Scale, Waiting Pricing.
        - Technical Office user role.
        - Scale data management on Products.
        - Integration with Smile Checklist for validation tasks.
    """,
    'author': 'Business Solutions',
    'website': 'https://www.thebusinesssolutions.net',
    'depends': ['sale', 'product', 'checklist'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}