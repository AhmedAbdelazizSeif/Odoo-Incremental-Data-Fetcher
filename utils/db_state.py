"""
Database State Manager
Manages tracking of ETL state (max IDs, counts, etc).
"""

import json
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DBStateManager:
    """Manages ETL state and database metadata."""
    
    def __init__(self, engine: create_engine, state_file: str = 'db_vars.json'):
        """
        Initialize state manager.
        
        Args:
            engine: SQLAlchemy engine
            state_file: Path to state file
        """
        self.engine = engine
        self.state_file = Path(state_file)
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load state file: {e}")
                return {}
        return {}
    
    def save_state(self):
        """Save current state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            logger.info(f"State saved to {self.state_file}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def get_max_id(self, table: str, id_column: str = 'id', 
                   prefix: str = None) -> int:
        """
        Get maximum ID from a table.
        
        Args:
            table: Table name
            id_column: ID column name
            prefix: Optional prefix to strip (e.g., 'POS-', 'DS-')
            
        Returns:
            Maximum ID value
        """
        try:
            with self.engine.connect() as conn:
                if prefix:
                    query = text(f"""
                        SELECT COALESCE(
                            MAX(CAST(SUBSTRING({id_column} FROM LENGTH('{prefix}') + 1) AS INTEGER)),
                            0
                        ) as max_id
                        FROM {table}
                        WHERE {id_column} LIKE '{prefix}%'
                    """)
                else:
                    query = text(f"""
                        SELECT COALESCE(MAX({id_column}), 0) as max_id
                        FROM {table}
                    """)
                
                result = conn.execute(query)
                max_id = result.scalar()
                logger.info(f"Max ID in {table}.{id_column}: {max_id}")
                return int(max_id) if max_id else 0
        
        except Exception as e:
            logger.error(f"Error getting max ID from {table}: {e}")
            return 0
    
    def get_existing_ids(self, table: str, id_column: str = 'id') -> list:
        """
        Get all existing IDs from a table.
        
        Args:
            table: Table name
            id_column: ID column name
            
        Returns:
            List of existing IDs
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT {id_column} FROM {table}"))
                return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error getting existing IDs from {table}: {e}")
            return []
    
    def update_max_ids(self):
        """Update all max IDs in state."""
        self.state['max_pos_order_id'] = self.get_max_id('all_sales', 'id', 'POS-')
        self.state['max_ds_order_id'] = self.get_max_id('all_sales', 'id', 'DS-')
        self.state['max_promotion_id'] = self.get_max_id('dim_promotions', 'promotion_id')
        self.state['max_branch_id'] = self.get_max_id('dim_branches_branch_ref', 'ref_id')
        self.state['max_stock_id'] = self.get_max_id('fact_stock', 'id') if self.state.get('latest_stock_id') else 0
        
        logger.info("Max IDs updated in state")
        self.save_state()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from state."""
        return self.state.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set value in state."""
        self.state[key] = value
    
    def update(self, data: Dict[str, Any]):
        """Update state with dictionary."""
        self.state.update(data)
