"""
Promotion API Module
Specialized API for promotion operations.
"""

import pandas as pd
from .connection import OdooConnection
from .model import OdooModel
from .domain_builder import DomainBuilder
from .dataframe_processor import DataFrameProcessor


class PromotionAPI:
    """Specialized API for promotion operations."""
    
    def __init__(self, connection: OdooConnection):
        self.connection = connection
        self.promotion = OdooModel(connection, 'pos.promotion')
    
    def get_promotions(self, active: bool = True, limit: int = None) -> pd.DataFrame:
        """
        Get promotions.
        
        Args:
            active: Filter by active status
            limit: Maximum records to return
            
        Returns:
            DataFrame with promotion data
        """
        domain = DomainBuilder()
        if active is not None:
            domain.equals('active', active)
        
        promotions = self.promotion.search_read(
            domain=domain.build(),
            fields=[
                'id', 'name', 'promotion_type_id', 'start_date', 'end_date',
                'discount_total_amount', 'applicable_amount', 'active'
            ],
            limit=limit
        )
        
        return DataFrameProcessor.flatten_records(promotions)
