"""
Domain Builder Module
Helper class for building Odoo search domains.
"""

from typing import List, Any


class DomainBuilder:
    """Helper class for building Odoo search domains."""
    
    def __init__(self):
        self.conditions = []
    
    def add(self, field: str, operator: str, value: Any) -> 'DomainBuilder':
        """Add a condition to the domain."""
        self.conditions.append([field, operator, value])
        return self
    
    def equals(self, field: str, value: Any) -> 'DomainBuilder':
        """Add equality condition."""
        return self.add(field, '=', value)
    
    def not_equals(self, field: str, value: Any) -> 'DomainBuilder':
        """Add not-equals condition."""
        return self.add(field, '!=', value)
    
    def greater_than(self, field: str, value: Any) -> 'DomainBuilder':
        """Add greater-than condition."""
        return self.add(field, '>', value)
    
    def less_than(self, field: str, value: Any) -> 'DomainBuilder':
        """Add less-than condition."""
        return self.add(field, '<', value)
    
    def greater_equal(self, field: str, value: Any) -> 'DomainBuilder':
        """Add greater-than-or-equal condition."""
        return self.add(field, '>=', value)
    
    def less_equal(self, field: str, value: Any) -> 'DomainBuilder':
        """Add less-than-or-equal condition."""
        return self.add(field, '<=', value)
    
    def like(self, field: str, value: str) -> 'DomainBuilder':
        """Add case-insensitive pattern match."""
        return self.add(field, 'ilike', value)
    
    def in_list(self, field: str, values: List) -> 'DomainBuilder':
        """Add 'in' condition."""
        return self.add(field, 'in', values)
    
    def date_range(self, field: str, start: str, end: str) -> 'DomainBuilder':
        """Add date range condition."""
        self.add(field, '>=', start)
        self.add(field, '<=', end)
        return self
    
    def build(self) -> List:
        """Build the final domain with AND logic."""
        if not self.conditions:
            return []
        if len(self.conditions) == 1:
            return self.conditions
        # Add AND operators between conditions
        return ['&'] * (len(self.conditions) - 1) + self.conditions
    
    def build_or(self) -> List:
        """Build the final domain with OR logic."""
        if not self.conditions:
            return []
        if len(self.conditions) == 1:
            return self.conditions
        # Add OR operators between conditions
        return ['|'] * (len(self.conditions) - 1) + self.conditions
