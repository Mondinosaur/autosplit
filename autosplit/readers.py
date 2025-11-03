"""Input file handling for AutoSplit."""
from __future__ import annotations
import os
from typing import Any, Optional

try:
    import pandas as pd
except ImportError:
    pd = None

def read_input(path: str, sheet: Optional[str] = None, header_row: Optional[int] = None) -> Any:
    """Read an input file and return a pandas DataFrame.
    
    Args:
        path: Path to the input file (.xlsx, .xls, or .csv)
        sheet: Sheet name for Excel files (optional)
        header_row: Row index (0-based) containing headers
    
    Returns:
        pandas.DataFrame: The loaded data
        
    Raises:
        RuntimeError: If pandas is not installed
        ValueError: If file type is unsupported or file cannot be read
    """
    print(f"\nReading input file: {path}")
    print(f"Sheet: {sheet}")
    print(f"Header row: {header_row}")
    if pd is None:
        raise RuntimeError("pandas is not installed. Please run: pip install -r requirements.txt")
        
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls", ".xlsm"):
        return _read_excel(path, sheet, header_row)
    elif ext == ".csv":
        return _read_csv(path)
    else:
        raise ValueError(f"Unsupported input file type: {ext}")

def _read_excel(path: str, sheet: Optional[str] = None, header_row: Optional[int] = None) -> Any:
    """Internal function to read Excel files."""
    try:
        # Read Excel info first
        print("\nReading Excel file...")
        xlsx = pd.read_excel(path, sheet_name=None, header=None)
        print("Available sheets:", list(xlsx.keys()))
        
        # If no sheet specified, use the first one
        if sheet is None:
            sheet = list(xlsx.keys())[0]
            print(f"Using first sheet: {sheet}")
        
        # Read the chosen sheet
        df = pd.read_excel(path, sheet_name=sheet, header=None)
        print(f"Initial shape: {df.shape}")
        
        # Find 'Product Code' column
        product_code_row = None
        product_code_col = None
        
        # Search for 'Product Code' in the first 10 rows
        for row_idx in range(min(10, len(df))):
            row = df.iloc[row_idx]
            for col_idx in range(len(row)):
                val = str(row.iloc[col_idx]).strip()
                if 'Product Code' in val:
                    product_code_row = row_idx
                    product_code_col = col_idx
                    print(f"Found 'Product Code' at row {row_idx}, column {col_idx}")
                    break
            if product_code_row is not None:
                break
                
        if product_code_row is None:
            raise ValueError("Could not find 'Product Code' in the first 10 rows")
            
        # Use the row with 'Product Code' as header
        headers = df.iloc[product_code_row]
        headers = headers.fillna('').astype(str).str.strip()
        
        # Keep only rows after the header
        df = df.iloc[product_code_row + 1:].copy()
        df.columns = headers
        
        # Clean up the data
        df = df.dropna(how='all')
        print(f"\nShape after removing empty rows: {df.shape}")
        
        # Fill NaN values with empty string
        df = df.fillna('')
        
        # Clean up the Product Code column
        df['Product Code'] = df['Product Code'].astype(str).str.strip()
        df = df[df['Product Code'] != '']
        print(f"\nRows with valid Product Codes: {len(df)}")
        print(f"Unique Product Codes found: {df['Product Code'].unique().tolist()}")
        
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        raise
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        raise

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

def _process_dataframe(df: Any, header_row: Optional[int] = None) -> Any:
    """Process the raw DataFrame to identify headers and clean data."""
    try:
        if header_row is not None:
            # Use the specified header row
            headers = df.iloc[header_row]
            df.columns = headers
            df = df.iloc[header_row + 1:].reset_index(drop=True)
        else:
            # Clean up existing column names
            df.columns = [str(col).strip() for col in df.columns]
        
        print("\nProcessed DataFrame info:")
        print(df.info())
        print("\nProcessed DataFrame preview:")
        print(df.head())
        print("\nColumns found:", list(df.columns))
        
        return df
    except Exception as e:
        print(f"Error processing DataFrame: {e}")
        raise