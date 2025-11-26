"""
Stock Extractor
Extracts stock/inventory data from Odoo.
"""

import pandas as pd
import itertools
import logging
from datetime import datetime
from odoo_client import OdooAPI, DomainBuilder

logger = logging.getLogger(__name__)


def extract_stock(api: OdooAPI, location_ids: list, latest_stock_id: int = 0, 
                  batch_size: int = 15000) -> tuple:
    """
    Extract stock quant data.
    
    Args:
        api: OdooAPI instance
        location_ids: List of location IDs to filter
        latest_stock_id: Maximum stock quant ID already in database
        batch_size: Records per batch
        
    Returns:
        Tuple of (stock_df, max_stock_id)
    """
    logger.info("Extracting stock data...")
    
    fields = 'id,location_id,product_id,reserved_quantity,available_quantity,in_date'.split(',')
    
    domain = DomainBuilder() \
        .add('id', '>', int(latest_stock_id)) \
        .add('location_id', 'in', location_ids) \
        .build()
    
    stock_quant_count = int(api.get_model('stock.quant').search_count(domain))
    logger.info(f"Total stock quants to extract: {stock_quant_count}")
    
    all_stock = []
    max_id = latest_stock_id
    
    for offset in range(0, stock_quant_count, batch_size):
        logger.info(f"Fetching stock batch: {offset} to {offset + batch_size}")
        
        stock_batch = pd.DataFrame(
            api.get_model('stock.quant').search_read(
                domain=domain,
                fields=fields,
                limit=batch_size,
                offset=offset
            )
        )
        
        if stock_batch.empty:
            continue
        
        # Process relational fields
        stock_batch['location_id'] = stock_batch['location_id'].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 1 else None
        )
        stock_batch['product_id'] = stock_batch['product_id'].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 1 else None
        )
        
        # Calculate last stocked days
        stock_batch['in_date'] = pd.to_datetime(stock_batch['in_date'], errors='coerce')
        stock_batch['last_stocked'] = stock_batch['in_date'].apply(
            lambda x: (datetime.now() - x).days if isinstance(x, pd.Timestamp) else None
        )
        
        max_id = max(max_id, stock_batch['id'].max())
        
        # Clean up
        stock_batch = stock_batch.drop(columns=['in_date', 'id'])
        stock_batch['product_id'] = stock_batch['product_id'].astype('int64')
        stock_batch['location_id'] = stock_batch['location_id'].astype('int64')
        
        all_stock.append(stock_batch)
    
    stock_df = pd.concat(all_stock, ignore_index=True) if all_stock else pd.DataFrame()
    
    logger.info(f"Extracted {len(stock_df)} stock records (max ID: {max_id})")
    return stock_df, max_id


def create_zero_stock_records(product_ids: list, location_ids: list, 
                              existing_stock_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create zero stock records for all product-location combinations not in stock.
    
    Args:
        product_ids: List of product IDs
        location_ids: List of location IDs
        existing_stock_df: DataFrame with existing stock records
        
    Returns:
        DataFrame with zero stock records
    """
    logger.info("Creating zero stock records for missing combinations...")
    
    # Create all possible combinations
    all_combinations = list(itertools.product(product_ids, location_ids))
    stock_0_df = pd.DataFrame(all_combinations, columns=['product_id', 'location_id'])
    stock_0_df['available_quantity'] = 0
    stock_0_df['reserved_quantity'] = 0
    stock_0_df['last_stocked'] = 0
    
    # Remove existing combinations
    stock_0_df = stock_0_df.merge(
        existing_stock_df[['product_id', 'location_id']],
        on=['product_id', 'location_id'],
        how='left',
        indicator=True
    )
    
    stock_0_df = stock_0_df[stock_0_df['_merge'] == 'left_only'].drop(columns=['_merge'])
    
    logger.info(f"Created {len(stock_0_df)} zero stock records")
    return stock_0_df
