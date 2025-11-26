"""
Categories Extractor
Extracts product categories and POS categories from Odoo.
"""

import pandas as pd
import logging
from odoo_client import OdooAPI

logger = logging.getLogger(__name__)


def extract_categories(api: OdooAPI) -> tuple:
    """
    Extract category data from Odoo.
    
    Args:
        api: OdooAPI instance
        
    Returns:
        Tuple of (product_categories_df, brands_df, pos_categories_df)
    """
    logger.info("Extracting categories...")
    
    # Product categories
    categories_count = int(api.get_model('product.category').search_count([]))
    logger.info(f"Extracting {categories_count} product categories")
    
    dim_categories = pd.DataFrame(
        api.get_model('product.category').search_read(
            domain=[],
            fields=['id', 'name', 'parent_id'],
            limit=categories_count
        )
    )
    dim_categories['parent_id'] = dim_categories['parent_id'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )
    dim_categories.rename(columns={
        'id': 'category_id',
        'name': 'category_name',
        'parent_id': 'category_parent',
    }, inplace=True)
    
    # Brands
    brands_count = int(api.get_model('product.brand').search_count([]))
    logger.info(f"Extracting {brands_count} brands")
    
    dim_brands = pd.DataFrame(
        api.get_model('product.brand').search_read(
            domain=[],
            fields=['id', 'name'],
            limit=brands_count
        )
    )
    dim_brands.rename(columns={
        'id': 'brand_id',
        'name': 'brand_name',
    }, inplace=True)
    
    # POS categories
    pos_categories_count = int(api.get_model('pos.category').search_count([]))
    logger.info(f"Extracting {pos_categories_count} POS categories")
    
    dim_pos_categories = pd.DataFrame(
        api.get_model('pos.category').search_read(
            domain=[],
            fields=['id', 'name'],
            limit=pos_categories_count
        )
    )
    dim_pos_categories.rename(columns={
        'id': 'category_id',
        'name': 'category_name',
    }, inplace=True)
    
    logger.info("Categories extraction complete")
    return dim_categories, dim_brands, dim_pos_categories
