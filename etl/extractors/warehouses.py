"""
Warehouses Extractor
Extracts warehouse and location data from Odoo.
"""

import pandas as pd
import logging
from odoo_client import OdooAPI, DomainBuilder

logger = logging.getLogger(__name__)


def extract_warehouses(api: OdooAPI) -> tuple:
    """
    Extract warehouse and stock location data.
    
    Args:
        api: OdooAPI instance
        
    Returns:
        Tuple of (warehouses_df, locations_df, internal_location_ids)
    """
    logger.info("Extracting warehouses and locations...")
    
    # Warehouses
    warehouse_count = int(api.get_model('stock.warehouse').search_count([
        ['active', '=', True]
    ]))
    
    fact_warehouse = pd.DataFrame(
        api.get_model('stock.warehouse').search_read(
            domain=[['active', '=', True]],
            fields=['id', 'name', 'code'],
            limit=warehouse_count
        )
    )
    
    # Extract numeric code
    fact_warehouse['code'] = fact_warehouse['code'].str.extract(
        r'(\d{3,4})'
    )[0].astype(float).fillna(0).astype(int)
    
    # Stock locations
    locations_domain = DomainBuilder() \
        .in_list('usage', ['internal', 'transit']) \
        .add('active', '=', True) \
        .build()
    
    stock_locations_count = int(api.get_model('stock.location').search_count(locations_domain))
    logger.info(f"Extracting {stock_locations_count} stock locations")
    
    stock_locations = pd.DataFrame(
        api.get_model('stock.location').search_read(
            domain=locations_domain,
            fields=['id', 'usage', 'warehouse_id'],
            limit=stock_locations_count
        )
    )
    
    stock_locations['warehouse_id'] = stock_locations['warehouse_id'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )
    
    internal_location_ids = stock_locations[
        stock_locations['usage'] == 'internal'
    ]['id'].tolist()
    
    logger.info(f"Extracted {len(fact_warehouse)} warehouses and {len(stock_locations)} locations")
    return fact_warehouse, stock_locations, internal_location_ids
