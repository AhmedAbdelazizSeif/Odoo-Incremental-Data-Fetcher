"""
Partner API Module
Specialized API for partner/customer operations.
"""

import pandas as pd
from .connection import OdooConnection
from .model import OdooModel
from .domain_builder import DomainBuilder
from .dataframe_processor import DataFrameProcessor


class PartnerAPI:
    """Specialized API for partner/customer operations."""
    
    def __init__(self, connection: OdooConnection):
        self.connection = connection
        self.partner = OdooModel(connection, 'res.partner')
    
    def search_partners(self, name: str = None, email: str = None,
                       phone: str = None, is_company: bool = None,
                       customer_rank: int = None, limit: int = 100) -> pd.DataFrame:
        """
        Search for partners/customers.
        
        Args:
            name: Partner name pattern
            email: Email address
            phone: Phone number
            is_company: Filter by company status
            customer_rank: Minimum customer rank
            limit: Maximum records to return
            
        Returns:
            DataFrame with partner data
        """
        domain = DomainBuilder()
        
        if name:
            domain.like('name', name)
        if email:
            domain.like('email', email)
        if phone:
            domain.like('phone', phone)
        if is_company is not None:
            domain.equals('is_company', is_company)
        if customer_rank is not None:
            domain.greater_equal('customer_rank', customer_rank)
        
        partners = self.partner.search_read(
            domain=domain.build(),
            fields=[
                'id', 'name', 'email', 'phone', 'mobile', 'street',
                'city', 'state_id', 'country_id', 'zip', 'is_company',
                'customer_rank', 'supplier_rank'
            ],
            limit=limit
        )
        
        return DataFrameProcessor.flatten_records(partners)
    
    def get_all_customers(self, batch_size: int = 1000) -> pd.DataFrame:
        """
        Get all customers in batches.
        
        Args:
            batch_size: Records per batch
            
        Returns:
            DataFrame with all customer data
        """
        all_customers = []
        offset = 0
        
        domain = DomainBuilder().greater_than('customer_rank', 0).build()
        
        while True:
            batch = self.partner.search_read(
                domain=domain,
                fields=[
                    'id', 'name', 'email', 'phone', 'mobile', 'street',
                    'city', 'state_id', 'country_id', 'zip', 'customer_rank'
                ],
                limit=batch_size,
                offset=offset
            )
            
            if not batch:
                break
            
            all_customers.extend(batch)
            offset += batch_size
        
        return DataFrameProcessor.flatten_records(all_customers)
