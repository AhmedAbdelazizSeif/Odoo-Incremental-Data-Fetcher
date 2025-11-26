"""
Odoo XML-RPC Client Library
A modular and optimized client for interacting with Odoo via XML-RPC.
"""

from .connection import OdooConnection
from .model import OdooModel
from .domain_builder import DomainBuilder
from .pos_api import POSOrderAPI
from .product_api import ProductAPI
from .partner_api import PartnerAPI
from .employee_api import EmployeeAPI
from .stock_api import StockAPI
from .promotion_api import PromotionAPI
from .api import OdooAPI

__version__ = "2.0.0"
__all__ = [
    "OdooConnection",
    "OdooModel",
    "DomainBuilder",
    "POSOrderAPI",
    "ProductAPI",
    "PartnerAPI",
    "EmployeeAPI",
    "StockAPI",
    "PromotionAPI",
    "OdooAPI",
]
