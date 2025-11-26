"""
Configuration Module
Manages configuration for Odoo and database connections.
All values must be provided via environment variables (.env file).
"""

import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for ETL pipeline."""
    
    # Odoo Configuration
    ODOO_URL = os.getenv('ODOO_URL')
    ODOO_DATABASE = os.getenv('ODOO_DATABASE')
    ODOO_USERNAME = os.getenv('ODOO_USERNAME')
    ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')
    
    # PostgreSQL Configuration
    POSTGRES_HOST = os.getenv('POSTGRES_HOST')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
    POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE')
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    
    # ETL Configuration
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '2500'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'odoo_etl.log')
    
    @classmethod
    def get_postgres_url(cls) -> str:
        """Get PostgreSQL connection URL."""
        return (
            f"postgresql+psycopg2://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
            f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DATABASE}"
        )
    
    @classmethod
    def get_odoo_config(cls) -> Dict[str, str]:
        """Get Odoo configuration as dictionary."""
        return {
            'url': cls.ODOO_URL,
            'database': cls.ODOO_DATABASE,
            'username': cls.ODOO_USERNAME,
            'password': cls.ODOO_PASSWORD
        }
