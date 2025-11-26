"""
Customers Extractor
Extracts customer/partner data from Odoo.
"""

import pandas as pd
import logging
from odoo_client import OdooAPI, DomainBuilder

logger = logging.getLogger(__name__)


def extract_customers(api: OdooAPI, existing_customer_ids: list = None, 
                     batch_size: int = 10000) -> pd.DataFrame:
    """
    Extract new customer data not already in database.
    
    Args:
        api: OdooAPI instance
        existing_customer_ids: List of customer IDs already in database
        batch_size: Records per batch
        
    Returns:
        DataFrame with new customer data
    """
    logger.info("Extracting customers...")
    
    if existing_customer_ids is None:
        existing_customer_ids = []
    
    new_customers_domain = DomainBuilder() \
        .add('id', 'not in', existing_customer_ids if existing_customer_ids else [0]) \
        .in_list('active', [True, False]) \
        .build()
    
    new_customers_count = int(api.get_model('res.partner').search_count(new_customers_domain))
    logger.info(f"Found {new_customers_count} new customers")
    
    all_customers = []
    
    for offset in range(0, new_customers_count, batch_size):
        logger.info(f"Fetching customers batch: {offset} to {offset + batch_size}")
        
        customers_batch = pd.DataFrame(
            api.get_model('res.partner').search_read(
                domain=new_customers_domain,
                fields=[
                    'id', 'display_name', 'email', 'phone', 'mobile', 'street', 
                    'street2', 'city', 'state_id', 'country_id', 'zip'
                ],
                limit=batch_size,
                offset=offset
            )
        )
        
        if customers_batch.empty:
            continue
        
        # Process relational fields
        relational_fields = ['state_id', 'country_id']
        for field in relational_fields:
            customers_batch[field] = customers_batch[field].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
            )
        
        # Truncate string fields to database limits
        customers_batch['phone'] = customers_batch['phone'].str[0:20]
        customers_batch['mobile'] = customers_batch['mobile'].str[0:20]
        customers_batch['display_name'] = customers_batch['display_name'].str[0:255]
        customers_batch['email'] = customers_batch['email'].str[0:100] if customers_batch['email'].dtype == object else ''
        customers_batch['street'] = customers_batch['street'].str[0:255] if customers_batch['street'].dtype == object else ''
        customers_batch['street2'] = customers_batch['street2'].str[0:255] if customers_batch['street2'].dtype == object else ''
        customers_batch['city'] = customers_batch['city'].str[0:100] if customers_batch['city'].dtype == object else ''
        customers_batch['zip'] = customers_batch['zip'].str[0:20] if customers_batch['zip'].dtype == object else ''
        
        all_customers.append(customers_batch)
    
    customers_df = pd.concat(all_customers, ignore_index=True) if all_customers else pd.DataFrame()
    
    logger.info(f"Extracted {len(customers_df)} new customers")
    return customers_df
