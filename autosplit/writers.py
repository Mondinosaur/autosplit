"""Output file generation for AutoSplit."""
from __future__ import annotations
import csv
import os
from typing import Any, Optional

try:
    import pandas as pd
except ImportError:
    pd = None

def ensure_dir(path: str) -> None:
    """Ensure a directory exists, creating it if necessary."""
    os.makedirs(path, exist_ok=True)

def write_group(df: Any, out_dir: str, filename: str, as_xlsx: bool = True) -> str:
    """Write a group DataFrame to a file.
    
    Args:
        df: Input DataFrame to write
        out_dir: Output directory path
        filename: Base filename (without extension)
        as_xlsx: Whether to write as Excel (True) or CSV (False)
    
    Returns:
        str: Path to written file
        
    Raises:
        RuntimeError: If pandas is not available for xlsx output
    """
    ensure_dir(out_dir)
    path = os.path.join(out_dir, filename)
    
    if as_xlsx:
        if pd is None:
            raise RuntimeError("pandas not available for writing xlsx")
        # pandas will pick an engine available (openpyxl/xlsxwriter)
        df.to_excel(path + (".xlsx" if not path.endswith('.xlsx') else ''), index=False)
        return path + (".xlsx" if not path.endswith('.xlsx') else '')
    else:
        df.to_csv(path + (".csv" if not path.endswith('.csv') else ''), 
                  index=False, 
                  quoting=csv.QUOTE_MINIMAL)
        return path + (".csv" if not path.endswith('.csv') else '')

def build_manifest_row(product_key: str, 
                      file_path: str, 
                      status: str, 
                      warnings: list[str]) -> list[str]:
    """Build a row for the manifest CSV.
    
    Args:
        product_key: Product identifier
        file_path: Path to the product's output file
        status: Processing status ('ok', 'warning', or 'error')
        warnings: List of warning messages
        
    Returns:
        list: Row for manifest CSV
    """
    return [product_key or '', file_path or '', status, '; '.join(warnings)]