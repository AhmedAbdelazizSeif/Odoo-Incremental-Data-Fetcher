"""
Branch Extractor
Extracts branch configuration data from Odoo.
"""

import pandas as pd
import logging
from odoo_client import OdooAPI, DomainBuilder

logger = logging.getLogger(__name__)


def extract_branches(api: OdooAPI, max_branch_id: int = 0) -> tuple:
    """
    Extract branch data from Odoo POS configurations.
    
    Args:
        api: OdooAPI instance
        max_branch_id: Maximum branch reference ID already in database
        
    Returns:
        Tuple of (branches_df, branch_refs_df, branch_team_mapping)
    """
    logger.info("Extracting branches...")
    
    domain = DomainBuilder() \
        .add('id', '>', int(max_branch_id)) \
        .in_list('active', [True]) \
        .build()
    
    active_branches = pd.DataFrame(
        api.get_model('pos.config').search_read(
            domain=domain,
            fields=['id', 'name', 'crm_team_id']
        )
    )
    
    if active_branches.empty:
        logger.info("No new branches found")
        return pd.DataFrame(), pd.DataFrame(), {}
    
    # Extract BranchID from name (e.g., "Branch 1001")
    active_branches["BranchID"] = active_branches['name'].str.extract(r'(\d{3,4})').astype(int)
    active_branches['Branch_Name'] = active_branches['name'].str.replace(
        r'\s*\d{3,4}\s*', '', regex=True
    ).str.replace('-', '').str.strip()
    
    # Process relational field
    active_branches['crm_team_id'] = active_branches['crm_team_id'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
    )
    
    # Prepare DataFrames
    branches_df = active_branches[['BranchID', 'Branch_Name']]
    branch_refs_df = active_branches[['id', 'BranchID', 'crm_team_id']].rename(
        columns={'id': 'ref_id', 'BranchID': 'branchid'}
    )
    
    # Create mapping dict for later use
    branch_team_mapping = active_branches.set_index('id')['crm_team_id'].to_dict()
    
    logger.info(f"Extracted {len(branches_df)} branches")
    return branches_df, branch_refs_df, branch_team_mapping
