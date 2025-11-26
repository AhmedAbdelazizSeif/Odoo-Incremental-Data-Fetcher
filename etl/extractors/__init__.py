"""
Extractors Package
Data extraction modules for different Odoo entities.
"""

from .branches import extract_branches
from .categories import extract_categories
from .products import extract_products
from .warehouses import extract_warehouses
from .stock import extract_stock
from .employees import extract_employees
from .customers import extract_customers
from .promotions import extract_promotions
from .sales import extract_sales, extract_sales_lines
from .purchases import extract_purchases

__all__ = [
    'extract_branches',
    'extract_categories',
    'extract_products',
    'extract_warehouses',
    'extract_stock',
    'extract_employees',
    'extract_customers',
    'extract_promotions',
    'extract_sales',
    'extract_sales_lines',
    'extract_purchases'
]
