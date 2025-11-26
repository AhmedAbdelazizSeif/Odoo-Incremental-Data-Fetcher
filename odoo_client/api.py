"""
Main Odoo API Module
Unified interface to all Odoo API modules.
"""

from typing import Dict, Any
from .connection import OdooConnection
from .model import OdooModel
from .pos_api import POSOrderAPI
from .product_api import ProductAPI
from .partner_api import PartnerAPI
from .employee_api import EmployeeAPI
from .stock_api import StockAPI
from .promotion_api import PromotionAPI


class OdooAPI:
    """
    Main Odoo API client providing unified access to all modules.
    
    Example usage:
        api = OdooAPI(
            url='https://erp.example.com',
            database='production',
            username='user@example.com',
            password='password'
        )
        
        if api.connect():
            orders_df = api.pos.get_orders(
                date_from='2024-01-01 00:00:00',
                limit=1000
            )
    """
    
    def __init__(self, url: str, database: str, username: str, password: str):
        """
        Initialize Odoo API.
        
        Args:
            url: Odoo instance URL
            database: Database name
            username: Username
            password: Password
        """
        self.connection = OdooConnection(url, database, username, password)
        self._pos = None
        self._products = None
        self._partners = None
        self._employees = None
        self._stock = None
        self._promotions = None
    
    def connect(self) -> bool:
        """
        Authenticate with Odoo server.
        
        Returns:
            bool: True if successful
        """
        return self.connection.authenticate()
    
    def get_version(self) -> Dict[str, Any]:
        """Get Odoo server version."""
        return self.connection.get_version()
    
    @property
    def pos(self) -> POSOrderAPI:
        """Get POS API instance."""
        if not self._pos:
            self._pos = POSOrderAPI(self.connection)
        return self._pos
    
    @property
    def products(self) -> ProductAPI:
        """Get Product API instance."""
        if not self._products:
            self._products = ProductAPI(self.connection)
        return self._products
    
    @property
    def partners(self) -> PartnerAPI:
        """Get Partner API instance."""
        if not self._partners:
            self._partners = PartnerAPI(self.connection)
        return self._partners
    
    @property
    def employees(self) -> EmployeeAPI:
        """Get Employee API instance."""
        if not self._employees:
            self._employees = EmployeeAPI(self.connection)
        return self._employees
    
    @property
    def stock(self) -> StockAPI:
        """Get Stock API instance."""
        if not self._stock:
            self._stock = StockAPI(self.connection)
        return self._stock
    
    @property
    def promotions(self) -> PromotionAPI:
        """Get Promotion API instance."""
        if not self._promotions:
            self._promotions = PromotionAPI(self.connection)
        return self._promotions
    
    def get_model(self, model_name: str) -> OdooModel:
        """
        Get a generic model interface.
        
        Args:
            model_name: Odoo model name
            
        Returns:
            OdooModel instance
        """
        return OdooModel(self.connection, model_name)
