"""
POS Order API Module
Specialized API for Point of Sale operations.
"""

import pandas as pd
from typing import List
from .connection import OdooConnection
from .model import OdooModel
from .domain_builder import DomainBuilder
from .dataframe_processor import DataFrameProcessor


class POSOrderAPI:
    """Specialized API for POS (Point of Sale) operations."""
    
    def __init__(self, connection: OdooConnection):
        self.connection = connection
        self.pos_order = OdooModel(connection, 'pos.order')
        self.pos_order_line = OdooModel(connection, 'pos.order.line')
        self.pos_session = OdooModel(connection, 'pos.session')
    
    def get_orders(self, date_from: str = None, date_to: str = None,
                   session_id: int = None, employee_id: int = None,
                   partner_id: int = None, state: str = None,
                   limit: int = None, offset: int = 0) -> pd.DataFrame:
        """
        Get POS orders with filters.
        
        Args:
            date_from: Start date (YYYY-MM-DD HH:MM:SS)
            date_to: End date (YYYY-MM-DD HH:MM:SS)
            session_id: Filter by session
            employee_id: Filter by employee
            partner_id: Filter by customer
            state: Filter by state
            limit: Maximum records to return
            offset: Number of records to skip
            
        Returns:
            DataFrame with order data
        """
        domain = DomainBuilder()
        
        if date_from and date_to:
            domain.date_range('date_order', date_from, date_to)
        elif date_from:
            domain.greater_equal('date_order', date_from)
        elif date_to:
            domain.less_equal('date_order', date_to)
        
        if session_id:
            domain.equals('session_id', session_id)
        if employee_id:
            domain.equals('employee_id', employee_id)
        if partner_id:
            domain.equals('partner_id', partner_id)
        if state:
            domain.equals('state', state)
        
        orders = self.pos_order.search_read(
            domain=domain.build(),
            fields=[
                'id', 'name', 'date_order', 'session_id', 'partner_id',
                'employee_id', 'amount_total', 'amount_tax', 'state',
                'user_id', 'lines', 'payment_ids'
            ],
            limit=limit,
            offset=offset
        )
        
        return DataFrameProcessor.flatten_records(orders)
    
    def get_order_lines(self, order_ids: List[int] = None, 
                       date_from: str = None, date_to: str = None,
                       product_id: int = None, limit: int = None) -> pd.DataFrame:
        """
        Get POS order lines with filters.
        
        Args:
            order_ids: Filter by order IDs
            date_from: Start date for order date
            date_to: End date for order date
            product_id: Filter by product
            limit: Maximum records to return
            
        Returns:
            DataFrame with order line data
        """
        domain = DomainBuilder()
        
        if order_ids:
            domain.in_list('order_id', order_ids)
        if date_from:
            domain.greater_equal('order_id.date_order', date_from)
        if date_to:
            domain.less_equal('order_id.date_order', date_to)
        if product_id:
            domain.equals('product_id', product_id)
        
        lines = self.pos_order_line.search_read(
            domain=domain.build(),
            fields=[
                'id', 'order_id', 'product_id', 'qty', 'price_unit',
                'price_subtotal', 'price_subtotal_incl', 'discount',
                'total_cost', 'promotion_id'
            ],
            limit=limit
        )
        
        return DataFrameProcessor.flatten_records(lines, prefix='line_')
    
    def get_orders_with_lines(self, date_from: str = None, date_to: str = None,
                             limit: int = None, offset: int = 0) -> pd.DataFrame:
        """
        Get POS orders combined with their order lines.
        
        Args:
            date_from: Start date
            date_to: End date
            limit: Maximum orders to return
            offset: Number of records to skip
            
        Returns:
            DataFrame with combined order and line data
        """
        orders_df = self.get_orders(
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        
        if orders_df.empty:
            return pd.DataFrame()
        
        order_ids = orders_df['id'].tolist()
        lines_df = self.get_order_lines(order_ids=order_ids)
        
        if lines_df.empty:
            return orders_df
        
        # Merge orders with lines
        orders_df = orders_df.rename(columns={'id': 'order_id'})
        
        combined = orders_df.merge(
            lines_df,
            on='order_id',
            how='left'
        )
        
        return combined
