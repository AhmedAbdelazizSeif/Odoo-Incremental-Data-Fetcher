"""
Main ETL Pipeline
Orchestrates the complete ETL process from Odoo to PostgreSQL.
"""

import sys
import logging
from sqlalchemy import create_engine
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.config import Config
from utils.logging_config import setup_logging
from utils.db_state import DBStateManager
from odoo_client import OdooAPI
from etl.extractors import *
from etl.loaders import upsertion_method


def main():
    """Main ETL pipeline execution."""
    
    # Setup logging
    logger = setup_logging(Config.LOG_FILE, Config.LOG_LEVEL)
    logger.info("=" * 80)
    logger.info("Starting Odoo ETL Pipeline")
    logger.info("=" * 80)
    
    try:
        # Initialize database connection
        logger.info("Connecting to PostgreSQL database...")
        engine = create_engine(
            Config.get_postgres_url(),
            echo=False,
            pool_size=20,
            max_overflow=0,
            pool_timeout=30,
            pool_recycle=3600
        )
        
        # Initialize state manager
        state_manager = DBStateManager(engine)
        state_manager.update_max_ids()
        
        # Initialize Odoo API
        logger.info("Connecting to Odoo...")
        api = OdooAPI(**Config.get_odoo_config())
        
        if not api.connect():
            logger.error("Failed to connect to Odoo")
            return 1
        
        # Extract and load branches
        logger.info("\n" + "=" * 80)
        logger.info("BRANCHES")
        logger.info("=" * 80)
        max_branch_id = state_manager.get('max_branch_id', 0)
        branches_df, branch_refs_df, branch_mapping = extract_branches(api, max_branch_id)
        
        if not branches_df.empty:
            upsertion_method(branches_df, 'dim_branches', engine, ['BranchID'])
            upsertion_method(branch_refs_df, 'dim_branches_branch_ref', engine, ['ref_id'])
            state_manager.update(branch_mapping)
            state_manager.save_state()
        
        # Extract and load categories
        logger.info("\n" + "=" * 80)
        logger.info("CATEGORIES")
        logger.info("=" * 80)
        categories_df, brands_df, pos_categories_df = extract_categories(api)
        upsertion_method(categories_df, 'dim_categories', engine, ['category_id'])
        upsertion_method(brands_df, 'dim_brands', engine, ['brand_id'])
        upsertion_method(pos_categories_df, 'dim_pos_categories', engine, ['category_id'])
        
        # Extract and load products
        logger.info("\n" + "=" * 80)
        logger.info("PRODUCTS")
        logger.info("=" * 80)
        products_df, products_ref_df, active_product_ids = extract_products(
            api, batch_size=Config.BATCH_SIZE
        )
        upsertion_method(products_df, 'dim_products', engine, ['ref_id'])
        upsertion_method(products_ref_df, 'dim_products_product', engine, ['id'])
        
        # Extract and load warehouses
        logger.info("\n" + "=" * 80)
        logger.info("WAREHOUSES & LOCATIONS")
        logger.info("=" * 80)
        warehouses_df, locations_df, internal_location_ids = extract_warehouses(api)
        upsertion_method(warehouses_df, 'fact_warehouse', engine, ['id'])
        upsertion_method(locations_df, 'fact_stock_locations', engine, ['id'])
        
        # Extract and load stock
        logger.info("\n" + "=" * 80)
        logger.info("STOCK")
        logger.info("=" * 80)
        stock_df, max_stock_id = extract_stock(
            api, internal_location_ids, state_manager.get('latest_stock_id', 0)
        )
        if not stock_df.empty:
            upsertion_method(stock_df, 'fact_stock', engine, ['product_id', 'location_id'])
            state_manager.set('latest_stock_id', max_stock_id)
            state_manager.save_state()
        
        # Create zero stock records
        existing_stock = state_manager.get_existing_ids('fact_stock', 'product_id')
        zero_stock_df = create_zero_stock_records(
            active_product_ids, internal_location_ids, stock_df
        )
        if not zero_stock_df.empty:
            upsertion_method(zero_stock_df, 'fact_stock', engine, ['product_id', 'location_id'])
        
        # Extract and load employees
        logger.info("\n" + "=" * 80)
        logger.info("EMPLOYEES & HR DATA")
        logger.info("=" * 80)
        (departments_df, work_locations_df, jobs_df, 
         employees_df, users_df, teams_df) = extract_employees(api)
        
        upsertion_method(departments_df, 'dim_departments', engine, ['id'])
        upsertion_method(work_locations_df, 'dim_work_locations', engine, ['work_location_id'])
        upsertion_method(jobs_df, 'dim_jobs', engine, ['job_id'])
        upsertion_method(employees_df, 'dim_emps', engine, ['employee_id'])
        upsertion_method(users_df, 'dim_users', engine, ['id'])
        upsertion_method(teams_df, 'dim_teams', engine, ['id'])
        
        # Extract and load customers
        logger.info("\n" + "=" * 80)
        logger.info("CUSTOMERS")
        logger.info("=" * 80)
        existing_customers = state_manager.get_existing_ids('dim_customers', 'id')
        customers_df = extract_customers(api, existing_customers)
        if not customers_df.empty:
            upsertion_method(customers_df, 'dim_customers', engine, ['id'])
        
        # Extract and load promotions
        logger.info("\n" + "=" * 80)
        logger.info("PROMOTIONS")
        logger.info("=" * 80)
        max_promotion_id = state_manager.get('max_promotion_id', 0)
        promotions_df, promotion_types_df = extract_promotions(api, max_promotion_id)
        
        if not promotions_df.empty:
            upsertion_method(promotion_types_df, 'dim_promotion_types', engine, ['id'])
            upsertion_method(promotions_df, 'dim_promotions', engine, ['promotion_id'])
        
        # Extract and load sales
        logger.info("\n" + "=" * 80)
        logger.info("SALES ORDERS")
        logger.info("=" * 80)
        max_pos_id = state_manager.get('max_pos_order_id', 0)
        max_ds_id = state_manager.get('max_ds_order_id', 0)
        sales_df = extract_sales(api, max_pos_id, max_ds_id, state_manager.state)
        
        if not sales_df.empty:
            upsertion_method(sales_df, 'all_sales', engine, ['id'])
        
        # Extract and load sales lines
        logger.info("\n" + "=" * 80)
        logger.info("SALES LINES")
        logger.info("=" * 80)
        missing_lines_query = """
            SELECT CAST(SUBSTRING(all_sales.id FROM 5) AS INTEGER) as id 
            FROM all_sales 
            LEFT JOIN fact_sales_lines ON all_sales.id = fact_sales_lines.order_id 
            WHERE fact_sales_lines.id IS NULL AND all_sales.id LIKE 'POS-%'
        """
        sales_lines_df = extract_sales_lines(api, engine, missing_lines_query)
        
        if not sales_lines_df.empty:
            upsertion_method(sales_lines_df, 'fact_sales_lines', engine, ['id'])
        
        # Extract and load purchases
        logger.info("\n" + "=" * 80)
        logger.info("PURCHASE ORDERS")
        logger.info("=" * 80)
        purchases_df, purchase_lines_df, picking_types_df = extract_purchases(api)
        upsertion_method(picking_types_df, 'dim_stock_picking_type', engine, ['id'])
        upsertion_method(purchases_df, 'dim_purchases', engine, ['id'])
        upsertion_method(purchase_lines_df, 'fact_purchases', engine, ['id'])
        
        # Update state with final max IDs
        state_manager.update_max_ids()
        
        logger.info("\n" + "=" * 80)
        logger.info("ETL Pipeline Completed Successfully!")
        logger.info("=" * 80)
        return 0
    
    except Exception as e:
        logger.error(f"ETL Pipeline failed with error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
