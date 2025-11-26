"""
DataFrame Processor Module
Helper class for processing Odoo data into pandas DataFrames.
"""

import pandas as pd
from typing import List, Dict, Tuple


class DataFrameProcessor:
    """Helper class for processing Odoo data into pandas DataFrames."""
    
    @staticmethod
    def process_relational_field(series: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """
        Process a relational field into ID and name columns.
        
        Args:
            series: Series containing relational field data [id, name]
            
        Returns:
            Tuple of (id_series, name_series)
        """
        ids = series.apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
        names = series.apply(lambda x: x[1] if isinstance(x, list) and len(x) > 1 else None)
        return ids, names
    
    @staticmethod
    def flatten_records(records: List[Dict], prefix: str = '') -> pd.DataFrame:
        """
        Flatten Odoo records into a DataFrame, handling relational fields.
        
        Args:
            records: List of record dictionaries
            prefix: Prefix to add to column names
            
        Returns:
            Flattened DataFrame
        """
        if not records:
            return pd.DataFrame()
        
        df = pd.DataFrame(records)
        
        # Process relational fields (Many2one fields that return [id, name])
        for col in df.columns:
            if df[col].dtype == object:
                sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                if isinstance(sample, list) and len(sample) == 2:
                    # Split into ID and name
                    df[f'{prefix}{col}_id'], df[f'{prefix}{col}_name'] = \
                        DataFrameProcessor.process_relational_field(df[col])
                    df.drop(columns=[col], inplace=True)
        
        # Add prefix to all columns if specified
        if prefix:
            df.columns = [f'{prefix}{col}' if not col.startswith(prefix) else col 
                         for col in df.columns]
        
        return df
