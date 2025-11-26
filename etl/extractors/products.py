"""
Products Extractor
Extracts product data from Odoo.
"""

import pandas as pd
import logging
from odoo_client import OdooAPI, DomainBuilder

logger = logging.getLogger(__name__)


def extract_products(api: OdooAPI, batch_size: int = 2500) -> tuple:
    """
    Extract product data from Odoo in batches.
    
    Args:
        api: OdooAPI instance
        batch_size: Number of records per batch
        
    Returns:
        Tuple of (products_df, products_ref_df, active_product_ids)
    """
    logger.info("Extracting products...")
    
    products_fields = [
        'id', 'create_date', 'default_code', 'name', 'list_price', 
        'activity_state', 'standard_price', 'pos_categ_id', 'categ_id', 
        'uom_id', 'active', 'sale_ok', 'purchase_ok', 'available_in_pos',
        'barcode', 'last_purchase_price', 'location_of_supply', 'brand_id',
        'end_trans', 'description', 'product_tmpl_id'
    ]
    
    domain = DomainBuilder().in_list('active', [True, False]).build()
    products_count = int(api.get_model('product.product').search_count(domain))
    logger.info(f"Total products to extract: {products_count}")
    
    all_products = []
    all_products_ref = []
    active_product_ids = []
    
    for offset in range(0, products_count, batch_size):
        logger.info(f"Fetching products batch: {offset} to {offset + batch_size}")
        
        products_batch = pd.DataFrame(
            api.get_model('product.product').search_read(
                domain=domain,
                fields=products_fields,
                limit=batch_size,
                offset=offset
            )
        )
        
        # Process relational fields
        relational_fields = ['pos_categ_id', 'categ_id', 'brand_id', 'product_tmpl_id']
        for field in relational_fields:
            products_batch[field] = products_batch[field].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
            )
        
        # Process uom_id (returns [id, name])
        products_batch['uom_id'] = products_batch['uom_id'].apply(
            lambda x: x[1] if isinstance(x, list) and len(x) > 0 else None
        )
        
        # Calculate product age
        products_batch['product_age'] = (
            pd.to_datetime('today') - pd.to_datetime(products_batch['create_date'])
        ).dt.days
        
        # Prepare dimension table
        dim_products = products_batch.rename(columns={
            'product_tmpl_id': 'ref_id',
            'default_code': 'product_id',
            'name': 'product_name',
            'list_price': 'product_price',
            'uom_id': 'unit_of_measure',
            'categ_id': 'category_id',
        }).copy()
        
        dim_products = dim_products[[
            'ref_id', 'product_id', 'product_name', 'product_price',
            'activity_state', 'standard_price', 'active', 'sale_ok', 'pos_categ_id',
            'purchase_ok', 'unit_of_measure', 'category_id', 'available_in_pos',
            'brand_id', 'barcode', 'last_purchase_price', 'end_trans',
            'product_age', 'location_of_supply'
        ]]
        
        # Track active product IDs
        active_product_ids.extend(
            products_batch[products_batch['active'] == True]['id'].tolist()
        )
        
        # Prepare reference table
        products_ref = products_batch[['id', 'product_tmpl_id']]
        
        all_products.append(dim_products)
        all_products_ref.append(products_ref)
    
    products_df = pd.concat(all_products, ignore_index=True)
    products_ref_df = pd.concat(all_products_ref, ignore_index=True)
    
    logger.info(f"Extracted {len(products_df)} products ({len(active_product_ids)} active)")
    return products_df, products_ref_df, active_product_ids
