"""
Stock API Module
Specialized API for stock/inventory operations.
"""

import pandas as pd
from .connection import OdooConnection
from .model import OdooModel
from .domain_builder import DomainBuilder
from .dataframe_processor import DataFrameProcessor


class StockAPI:
    """Specialized API for stock/inventory operations."""
    
    def __init__(self, connection: OdooConnection):
        self.connection = connection
        self.stock_quant = OdooModel(connection, 'stock.quant')
        self.stock_location = OdooModel(connection, 'stock.location')
    
    def get_stock(self, product_id: int = None, location_id: int = None,
                 available_only: bool = False, limit: int = None) -> pd.DataFrame:
        """
        Get stock/inventory data.
        
        Args:
            product_id: Filter by product
            location_id: Filter by location
            available_only: Only show available stock
            limit: Maximum records to return
            
        Returns:
            DataFrame with stock data
        """
        domain = DomainBuilder()
        
        if product_id:
            domain.equals('product_id', product_id)
        if location_id:
            domain.equals('location_id', location_id)
        if available_only:
            domain.greater_than('available_quantity', 0)
        
        stock = self.stock_quant.search_read(
            domain=domain.build(),
            fields=[
                'id', 'product_id', 'location_id', 'quantity',
                'available_quantity', 'reserved_quantity', 'in_date'
            ],
            limit=limit
        )
        
        return DataFrameProcessor.flatten_records(stock)
