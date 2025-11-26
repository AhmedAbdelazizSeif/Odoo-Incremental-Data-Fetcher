"""
Test Odoo Client
Unit tests for the Odoo client library.
"""

import pytest
from unittest.mock import Mock, patch
from odoo_client import OdooConnection, DomainBuilder


class TestDomainBuilder:
    """Test DomainBuilder functionality."""
    
    def test_simple_condition(self):
        """Test building a simple domain."""
        domain = DomainBuilder().equals('name', 'Test').build()
        assert domain == [['name', '=', 'Test']]
    
    def test_multiple_conditions_and(self):
        """Test building domain with AND logic."""
        domain = DomainBuilder() \
            .equals('active', True) \
            .greater_than('price', 100) \
            .build()
        assert domain == ['&', ['active', '=', True], ['price', '>', 100]]
    
    def test_multiple_conditions_or(self):
        """Test building domain with OR logic."""
        domain = DomainBuilder() \
            .equals('active', True) \
            .equals('draft', True) \
            .build_or()
        assert domain == ['|', ['active', '=', True], ['draft', '=', True]]
    
    def test_date_range(self):
        """Test date range condition."""
        domain = DomainBuilder() \
            .date_range('create_date', '2024-01-01', '2024-12-31') \
            .build()
        assert len(domain) == 3  # & operator + 2 conditions
    
    def test_in_list(self):
        """Test 'in' condition."""
        domain = DomainBuilder() \
            .in_list('state', ['draft', 'done']) \
            .build()
        assert domain == [['state', 'in', ['draft', 'done']]]


class TestOdooConnection:
    """Test OdooConnection class."""
    
    def test_initialization(self):
        """Test connection initialization."""
        conn = OdooConnection(
            url='https://example.com',
            database='test_db',
            username='user',
            password='pass'
        )
        assert conn.url == 'https://example.com'
        assert conn.database == 'test_db'
        assert conn.username == 'user'
        assert conn.uid is None
    
    @patch('xmlrpc.client.ServerProxy')
    def test_authenticate_success(self, mock_proxy):
        """Test successful authentication."""
        mock_common = Mock()
        mock_common.authenticate.return_value = 123
        mock_proxy.return_value = mock_common
        
        conn = OdooConnection(
            url='https://example.com',
            database='test_db',
            username='user',
            password='pass'
        )
        
        # Need to re-assign mocked proxy
        conn._common = mock_common
        
        result = conn.authenticate()
        assert result is True
        assert conn.uid == 123


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
