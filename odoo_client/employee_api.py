"""
Employee API Module
Specialized API for employee operations.
"""

import pandas as pd
from .connection import OdooConnection
from .model import OdooModel
from .domain_builder import DomainBuilder
from .dataframe_processor import DataFrameProcessor


class EmployeeAPI:
    """Specialized API for employee operations."""
    
    def __init__(self, connection: OdooConnection):
        self.connection = connection
        self.employee = OdooModel(connection, 'hr.employee')
    
    def get_all_employees(self, active: bool = True, limit: int = None) -> pd.DataFrame:
        """
        Get all employees.
        
        Args:
            active: Filter by active status
            limit: Maximum records to return
            
        Returns:
            DataFrame with employee data
        """
        domain = DomainBuilder()
        if active is not None:
            domain.equals('active', active)
        
        employees = self.employee.search_read(
            domain=domain.build(),
            fields=[
                'id', 'name', 'employee_code', 'job_id', 'department_id',
                'work_location_id', 'manager_id', 'active', 'birthday',
                'first_contract_date', 'gender'
            ],
            limit=limit
        )
        
        return DataFrameProcessor.flatten_records(employees)
