"""
Sales Extractor
Extracts POS and Direct Sales order data from Odoo.
"""

import pandas as pd
import numpy as np
import logging
from sqlalchemy import text
from odoo_client import OdooAPI, DomainBuilder

logger = logging.getLogger(__name__)


def extract_sales(api: OdooAPI, max_pos_id: int = 0, max_ds_id: int = 0, 
                 branch_team_mapping: dict = None) -> pd.DataFrame:
    """
    Extract POS and Direct Sales orders.
    
    Args:
        api: OdooAPI instance
        max_pos_id: Maximum POS order ID already in database
        max_ds_id: Maximum Direct Sales order ID already in database
        branch_team_mapping: Dict mapping config_id to team_id
        
    Returns:
        DataFrame with combined sales data
    """
    logger.info("Extracting sales orders...")
    
    if branch_team_mapping is None:
        branch_team_mapping = {}
    
    columns_for_all_sales = [
        'id', 'partner_id', 'employee_id', 'amount_total', 'order_in_hour',
        'amount_tax', 'date_order', 'user_id', 'config_id', 'channel', 
        'team_id', 'state'
    ]
    
    pos_main_cols = [
        'id', 'partner_id', 'employee_id', 'amount_total', 'order_in_hour',
        'amount_tax', 'date_order', 'user_id', 'config_id'
    ]
    
    ds_main_cols = [
        'id', 'partner_id', 'amount_total', 'amount_tax', 'date_order',
        'user_id', 'team_id', 'state', 'create_uid'
    ]
    
    all_sales = pd.DataFrame(columns=columns_for_all_sales)
    
    # Extract POS orders
    pos_domain = DomainBuilder().add('id', '>', int(max_pos_id)).build()
    pos_count = api.get_model('pos.order').search_count(pos_domain)
    logger.info(f"Extracting {pos_count} POS orders")
    
    if pos_count > 0:
        pos_orders = pd.DataFrame(
            api.get_model('pos.order').search_read(
                pos_domain,
                fields=pos_main_cols,
                limit=pos_count
            )
        )
        
        pos_orders['channel'] = 'in_store'
        
        # Process relational fields
        for field in ['partner_id', 'employee_id', 'user_id', 'config_id']:
            pos_orders[field] = pos_orders[field].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
            )
        
        pos_orders['team_id'] = pos_orders['config_id'].apply(
            lambda x: branch_team_mapping.get(x, None)
        )
        pos_orders['state'] = 'done'
        
        # Process dates
        pos_orders['date_order'] = pd.to_datetime(pos_orders['date_order']) \
            .dt.tz_localize('UTC').dt.tz_convert('Africa/Cairo').dt.tz_localize(None)
        pos_orders['order_in_hour'] = pos_orders['date_order'].dt.hour
        
        # Prefix ID with "POS-"
        pos_orders['id'] = pos_orders['id'].apply(lambda x: f"POS-{x}")
        
        all_sales = pd.concat([all_sales, pos_orders], ignore_index=True)
    
    # Extract Direct Sales orders
    ds_domain = DomainBuilder() \
        .add('id', '>', int(max_ds_id)) \
        .in_list('invoice_status', ['invoiced']) \
        .build()
    
    ds_count = api.get_model('sale.order').search_count(ds_domain)
    logger.info(f"Extracting {ds_count} Direct Sales orders")
    
    if ds_count > 0:
        ds_orders = pd.DataFrame(
            api.get_model('sale.order').search_read(
                ds_domain,
                fields=ds_main_cols,
                limit=ds_count
            )
        )
        
        # Process relational fields
        for field in ['create_uid', 'partner_id', 'user_id', 'team_id']:
            ds_orders[field] = ds_orders[field].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
            )
        
        # Determine channel (platform vs online)
        ds_orders['channel'] = np.where(ds_orders['create_uid'] == 1326, 'platform', 'online')
        # Specific partner IDs for platforms (Noon, Amazon, Trendyol)
        ds_orders['channel'] = np.where(
            ds_orders['partner_id'].isin([732481, 732480, 790176]), 
            'platform', 
            ds_orders['channel']
        )
        
        ds_orders['config_id'] = None
        
        # Process dates
        ds_orders['date_order'] = pd.to_datetime(ds_orders['date_order']) \
            .dt.tz_localize('UTC').dt.tz_convert('Africa/Cairo').dt.tz_localize(None)
        ds_orders['order_in_hour'] = ds_orders['date_order'].dt.hour
        
        # Prefix ID with "DS-"
        ds_orders['id'] = ds_orders['id'].apply(lambda x: f"DS-{x}")
        
        # Drop create_uid before concat
        ds_orders = ds_orders.drop(columns=['create_uid'])
        
        all_sales = pd.concat([all_sales, ds_orders], ignore_index=True)
    
    logger.info(f"Extracted total {len(all_sales)} sales orders")
    return all_sales


def extract_sales_lines(api: OdooAPI, engine, missing_order_ids_query: str = None) -> pd.DataFrame:
    """
    Extract sales order lines for orders missing line data.
    
    Args:
        api: OdooAPI instance
        engine: SQLAlchemy engine for database queries
        missing_order_ids_query: SQL query to find orders without lines
        
    Returns:
        DataFrame with sales lines
    """
    logger.info("Extracting sales lines...")
    
    if missing_order_ids_query is None:
        logger.warning("No query provided for missing order IDs")
        return pd.DataFrame()
    
    missing_lines = pd.read_sql(text(missing_order_ids_query), engine)['id'].tolist()
    
    if not missing_lines:
        logger.info("No missing sales lines found")
        return pd.DataFrame()
    
    logger.info(f"Found {len(missing_lines)} orders missing line data")
    
    all_lines = []
    batch_size = 15000
    
    for offset in range(0, len(missing_lines), batch_size):
        batch_ids = missing_lines[offset:offset + batch_size]
        
        lines_batch = pd.DataFrame(
            api.get_model('pos.order.line').search_read(
                domain=[['order_id', 'in', batch_ids]],
                fields=[
                    'id', 'order_id', 'product_id', 'qty', 'price_unit',
                    'price_subtotal', 'discount', 'promotion_id'
                ]
            )
        )
        
        all_lines.append(lines_batch)
    
    if not all_lines:
        return pd.DataFrame()
    
    lines_df = pd.concat(all_lines, ignore_index=True)
    
    # Process relational fields
    lines_df['product_id'] = lines_df['product_id'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )
    lines_df['promotion_id'] = lines_df['promotion_id'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )
    lines_df['order_id'] = lines_df['order_id'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )
    
    # Add prefix to order_id and id
    lines_df['order_id'] = lines_df['order_id'].apply(lambda x: f"POS-{x}")
    lines_df['id'] = lines_df['id'].apply(lambda x: f"POSL-{x}")
    
    logger.info(f"Extracted {len(lines_df)} sales lines")
    return lines_df
