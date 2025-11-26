"""
Purchases Extractor
Extracts purchase order data from Odoo.
"""

import pandas as pd
import logging
from odoo_client import OdooAPI, DomainBuilder

logger = logging.getLogger(__name__)


def extract_purchases(api: OdooAPI) -> tuple:
    """
    Extract purchase orders and purchase order lines.
    
    Args:
        api: OdooAPI instance
        
    Returns:
        Tuple of (purchase_orders_df, purchase_lines_df, picking_types_df)
    """
    logger.info("Extracting purchase orders...")
    
    # Purchase orders
    purchase_fields = [
        'id', 'partner_id', 'date_planned', 'origin', 'state',
        'effective_date', 'create_uid', 'picking_type_id'
    ]
    
    domain = DomainBuilder().add('invoice_status', '=', 'invoiced').build()
    purchase_count = int(api.get_model('purchase.order').search_count(domain))
    logger.info(f"Extracting {purchase_count} purchase orders")
    
    purchase_orders = pd.DataFrame(
        api.get_model('purchase.order').search_read(
            domain=domain,
            fields=purchase_fields,
            limit=purchase_count
        )
    )
    
    # Process relational fields
    for field in ['partner_id', 'create_uid', 'picking_type_id']:
        purchase_orders[field] = purchase_orders[field].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
        )
    
    # Process dates
    purchase_orders['date_planned'] = pd.to_datetime(purchase_orders['date_planned']) \
        .dt.tz_localize('UTC').dt.tz_convert('Africa/Cairo').dt.tz_localize(None)
    purchase_orders['effective_date'] = pd.to_datetime(
        purchase_orders['effective_date'], errors='coerce'
    ).dt.tz_localize('UTC').dt.tz_convert('Africa/Cairo').dt.tz_localize(None)
    
    purchase_orders['date_planned_hour'] = purchase_orders['date_planned'].dt.hour
    
    # Purchase order lines
    purchase_line_fields = [
        'id', 'order_id', 'product_id', 'product_qty', 'create_date',
        'date_order', 'date_approve', 'price_unit', 'price_subtotal', 'price_tax'
    ]
    
    line_domain = DomainBuilder().add(
        'order_id', 'in', purchase_orders['id'].tolist()
    ).build()
    
    purchase_lines_count = int(api.get_model('purchase.order.line').search_count(line_domain))
    logger.info(f"Extracting {purchase_lines_count} purchase order lines")
    
    purchase_lines = pd.DataFrame(
        api.get_model('purchase.order.line').search_read(
            domain=line_domain,
            fields=purchase_line_fields,
            limit=purchase_lines_count
        )
    )
    
    # Process relational fields
    for field in ['order_id', 'product_id']:
        purchase_lines[field] = purchase_lines[field].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
        )
    
    # Process dates
    purchase_lines['create_date'] = pd.to_datetime(purchase_lines['create_date']) \
        .dt.tz_localize('UTC').dt.tz_convert('Africa/Cairo').dt.tz_localize(None)
    purchase_lines['date_order'] = pd.to_datetime(purchase_lines['date_order']) \
        .dt.tz_localize('UTC').dt.tz_convert('Africa/Cairo').dt.tz_localize(None)
    purchase_lines['date_approve'] = pd.to_datetime(
        purchase_lines['date_approve'], errors='coerce'
    ).dt.tz_localize('UTC').dt.tz_convert('Africa/Cairo').dt.tz_localize(None)
    
    # Stock picking types
    picking_types_count = int(api.get_model('stock.picking.type').search_count([]))
    stock_picking_types = pd.DataFrame(
        api.get_model('stock.picking.type').search_read(
            domain=[],
            fields=['id', 'warehouse_id', 'name'],
            limit=picking_types_count
        )
    )
    stock_picking_types['warehouse_id'] = stock_picking_types['warehouse_id'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )
    
    logger.info("Purchase data extraction complete")
    return purchase_orders, purchase_lines, stock_picking_types
