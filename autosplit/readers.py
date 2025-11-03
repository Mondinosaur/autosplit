"""Input file handling for AutoSplit."""
from __future__ import annotations
import os
from typing import Any, Optional

try:
    import pandas as pd
except ImportError as e:
    print(f"Error importing pandas: {e}")
    pd = None

def read_input(path: str, sheet: Optional[str] = None) -> Any:
    """Read an input file and return a pandas DataFrame.
    
    Args:
        path: Path to the input file (.xlsx, .xls, or .csv)
        sheet: Sheet name for Excel files (optional)
    
    Returns:
        pandas.DataFrame: The loaded data
        
    Raises:
        RuntimeError: If pandas is not installed
        ValueError: If file type is unsupported or file cannot be read
    """
    if pd is None:
        raise RuntimeError("pandas is not installed. Please run: pip install -r requirements.txt")
        
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls"):
        return _read_excel(path, sheet)
    elif ext == ".csv":
        return _read_csv(path)
    else:
        raise ValueError(f"Unsupported input file type: {ext}")

def _read_excel(path: str, sheet: Optional[str] = None) -> Any:
    """Internal function to read Excel files."""
    # Read Excel info first
    xlsx = pd.read_excel(path, sheet_name=None, header=None)
    print("\nAvailable sheets:", list(xlsx.keys()))
    
    # If no sheet specified, use the first one
    if sheet is None:
        sheet = list(xlsx.keys())[0]
        print(f"Using first sheet: {sheet}")
    
    # Read the chosen sheet
    df = pd.read_excel(path, sheet_name=sheet, header=None)
    return _process_dataframe(df)

def _read_csv(path: str) -> Any:
    """Internal function to read CSV files with multiple encodings/delimiters."""
    encodings = ['utf-8', 'latin1', 'cp1252']
    delimiters = [',', ';', '\t']
    errors = []
    
    for encoding in encodings:
        for delimiter in delimiters:
            try:
                df = pd.read_csv(
                    path,
                    encoding=encoding,
                    sep=delimiter,
                    on_bad_lines='warn',
                    engine='python',
                    header=None
                )
                if len(df.columns) > 1:
                    print(f"Successfully read with encoding={encoding}, delimiter={delimiter}")
                    return _process_dataframe(df)
            except Exception as e:
                errors.append(f"Failed with encoding={encoding}, delimiter={delimiter}: {str(e)}")
                continue
    
    print("\nAttempted combinations:")
    for err in errors:
        print(f"  {err}")
    raise ValueError("Could not read CSV with any combination of encodings/delimiters")

def _process_dataframe(df: Any) -> Any:
    """Process the raw DataFrame to identify headers and clean data."""
    # Find the header row (look for 'Product Code' or similar)
    header_row = None
    for idx, row in df.iterrows():
        if any(str(cell).strip().lower() == 'product code' for cell in row if pd.notna(cell)):
            header_row = idx
            break
    
    if header_row is None:
        raise ValueError("Could not find header row with 'Product Code' column")
        
    print(f"\nFound headers at row {header_row}")
    
    # Use the identified header row
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:]  # Skip to data after header
    
    # Clean up column names
    df.columns = [str(col).strip() for col in df.columns]
    
    print("\nActual columns found:", list(df.columns))
    return df