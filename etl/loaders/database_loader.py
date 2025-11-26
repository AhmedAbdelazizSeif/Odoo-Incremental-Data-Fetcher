"""
Database Loader
Handles upsertion of data into PostgreSQL database with foreign key handling.
"""

import pandas as pd
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, PendingRollbackError

logger = logging.getLogger(__name__)


def upsertion_method(df: pd.DataFrame, table_name: str, engine: create_engine, 
                    primary_key: list, batch_size: int = 1000):
    """
    Upsert a DataFrame into a PostgreSQL table with foreign key violation handling.
    
    Args:
        df: DataFrame to upsert
        table_name: Name of the target table
        engine: SQLAlchemy engine
        primary_key: Primary key column names for upsert
        batch_size: Number of rows to process in each batch
    """
    
    def create_missing_data_table():
        """Create a table to log missing foreign key references."""
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS missing_data (
                    id SERIAL PRIMARY KEY,
                    foreign_key_name VARCHAR(255),
                    foreign_key_value VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
    
    def log_missing_foreign_key(foreign_key_name: str, foreign_key_value: str):
        """Log missing foreign key reference."""
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO missing_data (foreign_key_name, foreign_key_value)
                VALUES (:fk_name, :fk_value)
            """), {"fk_name": foreign_key_name, "fk_value": str(foreign_key_value)})
            conn.commit()
    
    def create_missing_foreign_key_record(foreign_key_name: str, foreign_key_value: str):
        """Create a placeholder record for missing foreign key."""
        # Extract table name from foreign key name
        # Assumes format like "fk_tablename_columnname"
        parts = foreign_key_name.split('_')
        if len(parts) >= 2:
            fk_table = '_'.join(parts[1:-1])  # Table name is between fk_ and last part
            fk_column = parts[-1]
            
            try:
                with engine.connect() as conn:
                    # Check if record exists
                    result = conn.execute(text(f"""
                        SELECT 1 FROM {fk_table} WHERE {fk_column} = :fk_value LIMIT 1
                    """), {"fk_value": foreign_key_value})
                    
                    if not result.fetchone():
                        # Create placeholder record
                        conn.execute(text(f"""
                            INSERT INTO {fk_table} ({fk_column}, name) 
                            VALUES (:fk_value, 'Unknown - Auto Created')
                            ON CONFLICT DO NOTHING
                        """), {"fk_value": foreign_key_value})
                        conn.commit()
                        logger.warning(f"Created placeholder record in {fk_table}")
            except Exception as e:
                logger.error(f"Failed to create placeholder record: {e}")
    
    def handle_foreign_key_violation(error_message: str):
        """Parse and handle foreign key violation errors."""
        try:
            # Extract foreign key details from error message
            if "violates foreign key constraint" in str(error_message):
                parts = str(error_message).split('"')
                if len(parts) >= 2:
                    constraint_name = parts[1]
                    # Extract value if present
                    if "Key (" in str(error_message):
                        value_part = str(error_message).split("Key (")[1].split(")")[0]
                        value = value_part.split("=")[1].strip() if "=" in value_part else "unknown"
                        
                        logger.warning(f"Foreign key violation: {constraint_name} = {value}")
                        log_missing_foreign_key(constraint_name, value)
                        create_missing_foreign_key_record(constraint_name, value)
        except Exception as e:
            logger.error(f"Error handling foreign key violation: {e}")
    
    def check_capitalization_issue(column_name: str):
        """Check if there are capitalization mismatches in column names."""
        return column_name.lower() if column_name != column_name.lower() else column_name
    
    def upsert_data():
        """Perform the actual upsert operation."""
        if isinstance(primary_key, str):
            pk_list = [primary_key]
        else:
            pk_list = primary_key
        
        # Normalize column names
        df_normalized = df.copy()
        df_normalized.columns = [check_capitalization_issue(col) for col in df_normalized.columns]
        
        # Build conflict clause
        conflict_cols = ', '.join(pk_list)
        update_cols = ', '.join([
            f"{col} = EXCLUDED.{col}" 
            for col in df_normalized.columns if col not in pk_list
        ])
        
        # Upsert in batches
        for i in range(0, len(df_normalized), batch_size):
            batch_df = df_normalized.iloc[i:i + batch_size]
            
            try:
                with engine.connect() as conn:
                    batch_df.to_sql(
                        table_name,
                        conn,
                        if_exists='append',
                        index=False,
                        method='multi'
                    )
                    
                    # Execute ON CONFLICT UPDATE
                    if update_cols:
                        conn.execute(text(f"""
                            INSERT INTO {table_name} ({', '.join(df_normalized.columns)})
                            SELECT {', '.join(df_normalized.columns)} FROM {table_name}_temp
                            ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_cols}
                        """))
                    
                    conn.commit()
                    logger.info(f"Upserted batch {i//batch_size + 1} into {table_name}")
            
            except IntegrityError as e:
                logger.error(f"Integrity error in batch {i//batch_size + 1}: {e}")
                handle_foreign_key_violation(str(e))
                raise
            
            except Exception as e:
                logger.error(f"Error upserting batch {i//batch_size + 1}: {e}")
                raise
    
    if df.empty:
        logger.info(f"DataFrame is empty, skipping upsert to {table_name}")
        return
    
    # Create missing_data table if it doesn't exist
    create_missing_data_table()
    
    max_retries = 2
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            upsert_data()
            logger.info(f"Successfully upserted {len(df)} records to {table_name}")
            break
        
        except (IntegrityError, PendingRollbackError) as e:
            retry_count += 1
            if retry_count >= max_retries:
                logger.error(f"Failed to upsert after {max_retries} retries: {e}")
                raise
            
            logger.warning(f"Retry {retry_count}/{max_retries} for {table_name}")
            handle_foreign_key_violation(str(e))
        
        except Exception as e:
            logger.error(f"Unexpected error during upsert to {table_name}: {e}")
            raise
    
    if retry_count >= max_retries:
        logger.error(f"Max retries exceeded for {table_name}")
