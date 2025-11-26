"""
Employees Extractor
Extracts employee and related HR data from Odoo.
"""

import pandas as pd
import logging
from odoo_client import OdooAPI, DomainBuilder

logger = logging.getLogger(__name__)


def extract_employees(api: OdooAPI) -> tuple:
    """
    Extract employee, department, job, and user data.
    
    Args:
        api: OdooAPI instance
        
    Returns:
        Tuple of (departments_df, work_locations_df, jobs_df, employees_df, users_df, teams_df)
    """
    logger.info("Extracting employee data...")
    
    # Departments
    departments_count = int(api.get_model('hr.department').search_count([]))
    dim_departments = pd.DataFrame(
        api.get_model('hr.department').search_read(
            domain=[],
            fields=['id', 'name', 'parent_id'],
            limit=departments_count
        )
    )
    dim_departments['parent_id'] = dim_departments['parent_id'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )
    
    # Work locations
    work_locations_count = int(api.get_model('hr.work.location').search_count([]))
    dim_work_locations = pd.DataFrame(
        api.get_model('hr.work.location').search_read(
            domain=[],
            fields=['id', 'name'],
            limit=work_locations_count
        )
    )
    dim_work_locations.rename(columns={
        'id': 'work_location_id',
        'name': 'work_location_name',
    }, inplace=True)
    
    # Jobs
    jobs_count = int(api.get_model('hr.job').search_count([]))
    dim_jobs = pd.DataFrame(
        api.get_model('hr.job').search_read(
            domain=[],
            fields=['id', 'name'],
            limit=jobs_count
        )
    )
    dim_jobs.rename(columns={
        'id': 'job_id',
        'name': 'job_name',
    }, inplace=True)
    
    # Employees
    employees_domain = DomainBuilder().in_list('active', [True, False]).build()
    employees_count = int(api.get_model('hr.employee').search_count(employees_domain))
    logger.info(f"Extracting {employees_count} employees")
    
    employee_fields = [
        'id', 'employee_code', 'name', 'first_contract_date',
        'department_id', 'job_id', 'parent_id', 'work_location_id', 
        'coach_id', 'active', 'country_id', 'gender', 'birthday', 
        'departure_date'
    ]
    
    dim_emps = pd.DataFrame(
        api.get_model('hr.employee').search_read(
            domain=employees_domain,
            fields=employee_fields,
            limit=employees_count
        )
    )
    
    # Process relational fields
    relational_fields = ['department_id', 'job_id', 'parent_id',
                        'work_location_id', 'coach_id', 'country_id']
    for field in relational_fields:
        dim_emps[field] = dim_emps[field].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
        )
    
    dim_emps.rename(columns={
        'id': 'employee_id',
        'name': 'employee_name',
        'parent_id': 'manager_id',
        'first_contract_date': 'hire_date',
        'country_id': 'country_id',
    }, inplace=True)
    
    # Calculate derived fields
    dim_emps['birthday'] = pd.to_datetime(dim_emps['birthday'], errors='coerce').fillna('2000-01-01')
    dim_emps['employee_age'] = (
        (pd.to_datetime('today') - pd.to_datetime(dim_emps['birthday'])).dt.days / 365.25
    ).astype(int)
    
    dim_emps['hire_date'] = pd.to_datetime(
        dim_emps['hire_date'].replace(False, pd.NaT).fillna(pd.Timestamp('2025-01-01'))
    )
    dim_emps['tenure_days'] = (pd.to_datetime('today') - dim_emps['hire_date']).dt.days
    dim_emps['departure_date'] = pd.to_datetime(dim_emps['departure_date'], errors='coerce')
    dim_emps['active'] = dim_emps['active'].astype(int)
    
    dim_emps = dim_emps[[
        'employee_id', 'employee_code', 'employee_name', 'hire_date',
        'employee_age', 'work_location_id', 'coach_id', 'department_id',
        'job_id', 'manager_id', 'country_id', 'active', 'departure_date',
        'tenure_days', 'gender'
    ]]
    
    # Users
    users_domain = DomainBuilder().in_list('active', [True, False]).build()
    users_count = int(api.get_model('res.users').search_count(users_domain))
    
    dim_users = pd.DataFrame(
        api.get_model('res.users').search_read(
            domain=users_domain,
            fields=['id', 'login', 'name', 'employee_id'],
            limit=users_count
        )
    ).rename(columns={'login': 'email'})
    
    dim_users['employee_id'] = dim_users['employee_id'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )
    
    # Teams
    teams_domain = DomainBuilder().in_list('active', [True, False]).build()
    teams_count = int(api.get_model('crm.team').search_count(teams_domain))
    
    dim_teams = pd.DataFrame(
        api.get_model('crm.team').search_read(
            domain=teams_domain,
            limit=teams_count,
            fields=['id', 'name', 'display_name', 'user_id', 'active'],
        )
    )
    dim_teams['user_id'] = dim_teams['user_id'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )
    dim_teams['branch_id'] = dim_teams['name'].str.extract(
        r'(\d{3,4})'
    ).astype(float).fillna(0).astype(int)
    dim_teams.drop(columns=['name'], inplace=True)
    
    logger.info("Employee data extraction complete")
    return dim_departments, dim_work_locations, dim_jobs, dim_emps, dim_users, dim_teams
