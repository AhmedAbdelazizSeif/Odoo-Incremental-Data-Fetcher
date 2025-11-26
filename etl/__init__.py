"""
ETL Package
Modular ETL pipeline for Odoo to PostgreSQL data synchronization.
"""

from .extractors import (
    extract_branches,
    extract_categories,
    extract_products,
    extract_warehouses,
    extract_stock,
    extract_employees,
    extract_customers,
    extract_promotions,
    extract_sales,
    extract_purchases
)

from .loaders import upsertion_method

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
    'extract_purchases',
    'upsertion_method'
]
