"""
Odoo Model Module
Base class for Odoo model operations.
"""

from typing import List, Dict, Any
from .connection import OdooConnection


class OdooModel:
    """Base class for Odoo model operations."""
    
    def __init__(self, connection: OdooConnection, model_name: str):
        """
        Initialize model interface.
        
        Args:
            connection: OdooConnection instance
            model_name: Name of the Odoo model
        """
        self.connection = connection
        self.model_name = model_name
    
    def search(self, domain: List = None, offset: int = 0, limit: int = None, 
               order: str = None) -> List[int]:
        """
        Search for record IDs matching domain.
        
        Args:
            domain: Search domain (e.g., [['is_company', '=', True]])
            offset: Number of records to skip
            limit: Maximum number of records
            order: Sort order
            
        Returns:
            List of record IDs
        """
        domain = domain or []
        kwargs = {'offset': offset}
        if limit is not None:
            kwargs['limit'] = limit
        if order:
            kwargs['order'] = order
            
        return self.connection.execute_kw(
            self.model_name, 'search', [domain], kwargs
        )
    
    def read(self, ids: List[int], fields: List[str] = None) -> List[Dict]:
        """
        Read records by IDs.
        
        Args:
            ids: List of record IDs
            fields: Fields to retrieve (None for all)
            
        Returns:
            List of record dictionaries
        """
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
            
        return self.connection.execute_kw(
            self.model_name, 'read', [ids], kwargs
        )
    
    def search_read(self, domain: List = None, fields: List[str] = None,
                    offset: int = 0, limit: int = None, order: str = None, 
                    lang: str = 'ar_001', import_compat: bool = False) -> List[Dict]:
        """
        Search and read records in one call.
        
        Args:
            domain: Search domain
            fields: Fields to retrieve
            offset: Number of records to skip
            limit: Maximum number of records
            order: Sort order
            lang: Language for context
            import_compat: Import compatibility mode
            
        Returns:
            List of record dictionaries
        """
        domain = domain or []
        kwargs = {'offset': offset}
        if fields:
            kwargs['fields'] = fields
        if limit is not None:
            kwargs['limit'] = limit
        if order:
            kwargs['order'] = order
        kwargs['context'] = {'lang': lang}
        if import_compat:
            kwargs['context']['import_compat'] = True
        
        return self.connection.execute_kw(
            self.model_name, 'search_read', [domain], kwargs
        )
    
    def read_group(self, domain: List = None, fields: List[str] = None,
                   offset: int = 0, limit: int = None, order: str = None, 
                   lang: str = 'ar_001', group_by: List[str] = None) -> List[Dict]:
        """
        Read grouped records.
        
        Args:
            domain: Search domain
            fields: Fields to retrieve
            offset: Number of records to skip
            limit: Maximum number of records
            order: Sort order
            lang: Language for context
            group_by: Fields to group by
            
        Returns:
            List of grouped record dictionaries
        """
        domain = domain or []
        kwargs = {'offset': offset}
        if fields:
            kwargs['fields'] = fields
        if limit is not None:
            kwargs['limit'] = limit
        if order:
            kwargs['order'] = order
        kwargs['context'] = {'lang': lang}
        if group_by:
            kwargs['groupby'] = group_by

        return self.connection.execute_kw(
            self.model_name, 'read_group', [domain], kwargs
        )

    def search_count(self, domain: List = None) -> int:
        """
        Count records matching domain.
        
        Args:
            domain: Search domain
            
        Returns:
            Number of matching records
        """
        domain = domain or []
        return self.connection.execute_kw(
            self.model_name, 'search_count', [domain]
        )
    
    def create(self, values: Dict) -> int:
        """
        Create a new record.
        
        Args:
            values: Field values for the new record
            
        Returns:
            ID of created record
        """
        return self.connection.execute_kw(
            self.model_name, 'create', [values]
        )
    
    def write(self, ids: List[int], values: Dict) -> bool:
        """
        Update records.
        
        Args:
            ids: Record IDs to update
            values: Field values to update
            
        Returns:
            True if successful
        """
        return self.connection.execute_kw(
            self.model_name, 'write', [ids, values]
        )
    
    def unlink(self, ids: List[int]) -> bool:
        """
        Delete records.
        
        Args:
            ids: Record IDs to delete
            
        Returns:
            True if successful
        """
        return self.connection.execute_kw(
            self.model_name, 'unlink', [ids]
        )
    
    def fields_get(self, fields: List[str] = None, 
                   attributes: List[str] = None) -> Dict:
        """
        Get field definitions for the model.
        
        Args:
            fields: Specific fields to get info for (None for all)
            attributes: Specific attributes to retrieve
            
        Returns:
            Dictionary of field definitions
        """
        args = [fields] if fields else []
        kwargs = {'attributes': attributes} if attributes else {}
        
        return self.connection.execute_kw(
            self.model_name, 'fields_get', args, kwargs
        )
