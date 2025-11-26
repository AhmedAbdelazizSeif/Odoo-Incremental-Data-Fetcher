"""
Product API Module
Specialized API for product operations.
"""

import pandas as pd
from .connection import OdooConnection
from .model import OdooModel
from .domain_builder import DomainBuilder
from .dataframe_processor import DataFrameProcessor


class ProductAPI:
    """Specialized API for product operations."""
    
    def __init__(self, connection: OdooConnection):
        self.connection = connection
        self.product_template = OdooModel(connection, 'product.template')
        self.product_product = OdooModel(connection, 'product.product')
    
    def search_products(self, name: str = None, barcode: str = None,
                       available_in_pos: bool = None, active: bool = True,
                       limit: int = 100) -> pd.DataFrame:
        """
        Search for products.
        
        Args:
            name: Product name pattern
            barcode: Product barcode
            available_in_pos: Filter by POS availability
            active: Filter by active status
            limit: Maximum records to return
            
        Returns:
            DataFrame with product data
        """
        domain = DomainBuilder()
        
        if name:
            domain.like('name', name)
        if barcode:
            domain.equals('barcode', barcode)
        if available_in_pos is not None:
            domain.equals('available_in_pos', available_in_pos)
        if active is not None:
            domain.equals('active', active)
        
        products = self.product_template.search_read(
            domain=domain.build(),
            fields=[
                'id', 'name', 'default_code', 'barcode', 'list_price',
                'standard_price', 'categ_id', 'pos_categ_id',
                'available_in_pos', 'active', 'uom_id'
            ],
            limit=limit
        )
        
        return DataFrameProcessor.flatten_records(products)
    
    def get_all_products(self, batch_size: int = 1000) -> pd.DataFrame:
        """
        Get all products in batches.
        
        Args:
            batch_size: Records per batch
            
        Returns:
            DataFrame with all product data
        """
        all_products = []
        offset = 0
        
        while True:
            batch = self.product_template.search_read(
                domain=[],
                fields=[
                    'id', 'name', 'default_code', 'barcode', 'list_price',
                    'standard_price', 'categ_id', 'pos_categ_id',
                    'available_in_pos', 'active', 'uom_id'
                ],
                limit=batch_size,
                offset=offset
            )
            
            if not batch:
                break
            
            all_products.extend(batch)
            offset += batch_size
        
        return DataFrameProcessor.flatten_records(all_products)
