"""
Odoo Connection Module
Manages XML-RPC connection and authentication with Odoo server.
"""

import xmlrpc.client
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class OdooConnection:
    """Manages XML-RPC connection and authentication with Odoo server."""
    
    def __init__(self, url: str, database: str, username: str, password: str):
        """
        Initialize Odoo connection.
        
        Args:
            url: Base URL of Odoo instance (e.g., 'https://erp.knozelhekma.com')
            database: Database name
            username: Username for authentication
            password: Password for authentication
        """
        self.url = url.rstrip('/')
        self.database = database
        self.username = username
        self.password = password
        self.uid = None
        
        # Initialize XML-RPC proxies
        self._common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self._models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        
    def authenticate(self) -> bool:
        """
        Authenticate with Odoo server.
        
        Returns:
            bool: True if authentication successful
        """
        try:
            self.uid = self._common.authenticate(
                self.database, self.username, self.password, {}
            )
            if self.uid:
                logger.info(f"✓ Authenticated successfully as {self.username} (UID: {self.uid})")
                return True
            else:
                logger.error("✗ Authentication failed: Invalid credentials")
                return False
        except Exception as e:
            logger.error(f"✗ Authentication error: {e}")
            return False
    
    def get_version(self) -> Dict[str, Any]:
        """Get Odoo server version information."""
        try:
            return self._common.version()
        except Exception as e:
            logger.error(f"Error getting version: {e}")
            return {}
    
    def execute_kw(self, model: str, method: str, args: List = None, 
                   kwargs: Dict = None) -> Any:
        """
        Execute a method on an Odoo model.
        
        Args:
            model: Odoo model name (e.g., 'pos.order', 'res.partner')
            method: Method to execute (e.g., 'search', 'read', 'create')
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Result of the method execution
        """
        if not self.uid:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        args = args or []
        kwargs = kwargs or {}
        
        try:
            return self._models.execute_kw(
                self.database,
                self.uid,
                self.password,
                model,
                method,
                args,
                kwargs
            )
        except Exception as e:
            logger.error(f"Error executing {method} on {model}: {e}")
            raise
