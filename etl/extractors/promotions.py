"""
Promotions Extractor
Extracts promotion data from Odoo.
"""

import pandas as pd
import numpy as np
import logging
from odoo_client import OdooAPI, DomainBuilder

logger = logging.getLogger(__name__)


def extract_promotions(api: OdooAPI, max_promotion_id: int = 0) -> tuple:
    """
    Extract promotion and promotion type data.
    
    Args:
        api: OdooAPI instance
        max_promotion_id: Maximum promotion ID already in database
        
    Returns:
        Tuple of (promotions_df, promotion_types_df)
    """
    logger.info("Extracting promotions...")
    
    domain = DomainBuilder().add('id', '>', int(max_promotion_id)).build()
    
    promotions = pd.DataFrame(
        api.get_model('pos.promotion').search_read(
            domain=domain,
            fields=[
                "id", "name", "applicable_amount", "discount_total_amount",
                "start_date", "end_date", "promotion_type_id", "x_promo_code",
                "x_magaine", "x_name", "state"
            ]
        )
    )
    
    if promotions.empty:
        logger.info("No new promotions found")
        return pd.DataFrame(), pd.DataFrame()
    
    logger.info(f"Found {len(promotions)} new promotions")
    
    # Extract promotion types
    promotion_types = pd.DataFrame(
        api.get_model('pos.promotion.type').search_read(
            domain=[],
            fields=["id", "name"]
        )
    )
    
    # Process promotions
    promotions['active'] = np.where(promotions['state'] == 'active', 1, 0)
    promotions = promotions.drop(columns=['state'])
    promotions.rename(columns={'id': 'promotion_id'}, inplace=True)
    
    promotions['promotion_type_id'] = promotions['promotion_type_id'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )
    
    # Convert dates to Cairo timezone
    promotions['start_date'] = pd.to_datetime(promotions['start_date']) \
        .dt.tz_localize('UTC').dt.tz_convert('Africa/Cairo').dt.tz_localize(None)
    promotions['end_date'] = pd.to_datetime(promotions['end_date']) \
        .dt.tz_localize('UTC').dt.tz_convert('Africa/Cairo').dt.tz_localize(None)
    
    logger.info(f"Extracted {len(promotions)} promotions and {len(promotion_types)} promotion types")
    return promotions, promotion_types
