"""Data processing functionality for AutoSplit."""
from __future__ import annotations
from typing import Any, Dict

try:
    import pandas as pd
except ImportError:
    pd = None

def split_by_key(df: Any, key_col: str) -> Dict[str, Any]:
    """Split DataFrame into groups based on a key column.
    
    Args:
        df: Input DataFrame
        key_col: Column name to group by
    
    Returns:
        dict: Mapping of keys to DataFrames
        
    Raises:
        KeyError: If key_col is not found in DataFrame
    """
    groups = {}
    if key_col not in df.columns:
        raise KeyError(f"Key column '{key_col}' not found in input headers: {list(df.columns)}")
    
    for key, g in df.groupby(key_col, dropna=False):
        # normalize key to string
        k = str(key).strip() if not (pd.isna(key)) else None
        groups[k or f"_unknown_{len(groups)+1}"] = g.dropna(how='all')
    return groups

def split_by_blocks(df: Any) -> Dict[str, Any]:
    """Split DataFrame into groups based on blank row separation.
    
    Args:
        df: Input DataFrame
    
    Returns:
        dict: Mapping of generated keys to DataFrames
    """
    groups = {}
    current_rows = []
    
    for _, row in df.iterrows():
        if row.isna().all():
            if current_rows:
                g = pd.DataFrame(current_rows)
                key = extract_block_key(g)
                groups[key] = g
                current_rows = []
        else:
            current_rows.append(row)
    
    if current_rows:
        g = pd.DataFrame(current_rows)
        key = extract_block_key(g)
        groups[key] = g
    
    return groups

def extract_block_key(g: Any) -> str:
    """Extract a meaningful key from a group DataFrame.
    
    Args:
        g: Input group DataFrame
    
    Returns:
        str: Generated key for the group
    """
    # attempt to find a column that looks like a title/product name
    for col in g.columns:
        # take first non-empty value
        vals = g[col].dropna().astype(str)
        if not vals.empty:
            candidate = vals.iloc[0].strip()
            if candidate:
                return candidate.replace('/', '_')[:80]
    return f"product_{len(g)}"

def get_default_key_column(df: Any) -> str:
    """Try to identify a suitable key column from common names.
    
    Args:
        df: Input DataFrame
    
    Returns:
        str: Name of identified key column
        
    Raises:
        ValueError: If no suitable key column is found
    """
    candidates = ["SKU", "sku", "Product ID", "Product", "product_name", "Name"]
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    raise ValueError("No suitable key column found")