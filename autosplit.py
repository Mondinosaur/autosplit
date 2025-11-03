#!/usr/bin/env python3
"""AutoSplit - scaffold implementation

Small CLI that reads an input .xlsx/.csv and writes one file per product
based on a key column or blank-row blocks. Produces outputs/manifest.csv.

This is a minimal, well-commented scaffold. It intentionally avoids heavy
third-party CLI frameworks to keep the dependency list small.
"""
from __future__ import annotations
import argparse
import csv
import os
import sys
from typing import List, Optional, Any

try:
    import pandas as pd
except Exception:
    pd = None  # handle gracefully at runtime


def read_input(path: str, sheet: Optional[str] = None) -> Any:
    if pd is None:
        raise RuntimeError("pandas is not installed. Please run: pip install -r requirements.txt")
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls"):
        # Read Excel info first
        xlsx = pd.read_excel(path, sheet_name=None, header=None)
        print("\nAvailable sheets:", list(xlsx.keys()))
        
        # If no sheet specified, use the first one
        if sheet is None:
            sheet = list(xlsx.keys())[0]
            print(f"Using first sheet: {sheet}")
        
        # Read the chosen sheet
        df = pd.read_excel(path, sheet_name=sheet, header=None)
        print(f"\nFirst 8 rows of sheet '{sheet}':")
        print(df.head(8))
        
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
    elif ext == ".csv":
        # Try different encodings and CSV parsing options
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
                        engine='python',  # More flexible but slower
                        header=None  # Read all rows as data first
                    )
                    if len(df.columns) > 1:  # Successfully parsed multiple columns
                        print(f"Successfully read with encoding={encoding}, delimiter={delimiter}")
                        # Use first row as headers
                        df.columns = df.iloc[0]
                        df = df.iloc[1:]  # Remove the header row
                        return df
                except Exception as e:
                    errors.append(f"Failed with encoding={encoding}, delimiter={delimiter}: {str(e)}")
                    continue
        
        print("\nAttempted combinations:")
        for err in errors:
            print(f"  {err}")
        raise ValueError("Could not read CSV with any combination of encodings/delimiters")
    else:
        raise ValueError(f"Unsupported input file type: {ext}")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def split_by_key(df: Any, key_col: str) -> dict:
    groups = {}
    if key_col not in df.columns:
        raise KeyError(f"Key column '{key_col}' not found in input headers: {list(df.columns)}")
    for key, g in df.groupby(key_col, dropna=False):
        # normalize key to string
        k = str(key).strip() if not (pd.isna(key)) else None
        groups[k or f"_unknown_{len(groups)+1}"] = g.dropna(how='all')
    return groups


def split_by_blocks(df: Any) -> dict:
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
    # attempt to find a column that looks like a title/product name
    for col in g.columns:
        # take first non-empty value
        vals = g[col].dropna().astype(str)
        if not vals.empty:
            candidate = vals.iloc[0].strip()
            if candidate:
                return candidate.replace('/', '_')[:80]
    return f"product_{len(g)}"


def validate_group(df: Any, min_images: int, image_cols: Optional[List[str]]) -> List[str]:
    warnings = []
    if image_cols:
        count = 0
        for c in image_cols:
            if c in df.columns:
                count += df[c].notna().sum()
        if count < min_images:
            warnings.append(f"Less than {min_images} image URLs ({count})")
    return warnings


def write_group(df: Any, out_dir: str, filename: str, as_xlsx: bool = True) -> str:
    ensure_dir(out_dir)
    path = os.path.join(out_dir, filename)
    if as_xlsx:
        if pd is None:
            raise RuntimeError("pandas not available for writing xlsx")
        # pandas will pick an engine available (openpyxl/xlsxwriter)
        df.to_excel(path + (".xlsx" if not path.endswith('.xlsx') else ''), index=False)
        return path + (".xlsx" if not path.endswith('.xlsx') else '')
    else:
        df.to_csv(path + (".csv" if not path.endswith('.csv') else ''), index=False, quoting=csv.QUOTE_MINIMAL)
        return path + (".csv" if not path.endswith('.csv') else '')


def build_manifest_row(product_key: str, file_path: str, status: str, warnings: List[str]) -> List[str]:
    return [product_key or '', file_path or '', status, '; '.join(warnings)]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog='autosplit', description='Split multi-product sheets into per-product files')
    parser.add_argument('input', help='Input .xlsx or .csv file (or a folder)')
    parser.add_argument('--key-col', help='Column name to group by (e.g. SKU)')
    parser.add_argument('--block', action='store_true', help='Split by blank-row blocks instead of a key column')
    parser.add_argument('--sheet', default=None, help='Sheet name or index (for xlsx)')
    parser.add_argument('--min-images', type=int, default=0, help='Minimum number of image URLs expected')
    parser.add_argument('--image-cols', help='Comma-separated list of image columns to check')
    parser.add_argument('--keep-empty-cols', action='store_true')
    parser.add_argument('--xlsx', action='store_true', help='Write output XLSX (default)')
    parser.add_argument('--output-dir', default='outputs', help='Directory to write outputs')

    args = parser.parse_args(argv)

    input_path = args.input
    out_dir = args.output_dir
    ensure_dir(out_dir)

    image_cols = args.image_cols.split(',') if args.image_cols else None

    # read
    try:
        df = read_input(input_path, sheet=args.sheet)
    except Exception as e:
        print(f"ERROR: failed to read input '{input_path}': {e}")
        return 2

    # if a sheet name returns a dict (pandas read_excel can return dict for sheet_name=None)
    if isinstance(df, dict):
        # pick the first sheet
        first_key = list(df.keys())[0]
        df = df[first_key]

    if df is None or df.empty:
        print("No rows found in input file.")
        return 1

    # split
    groups = {}
    try:
        if args.key_col:
            groups = split_by_key(df, args.key_col)
        elif args.block:
            groups = split_by_blocks(df)
        else:
            # default: if there's a single obvious key column try common names
            for candidate in ("SKU", "sku", "Product ID", "Product", "product_name", "Name"):
                if candidate in df.columns:
                    groups = split_by_key(df, candidate)
                    break
            if not groups:
                # fallback: treat each row as a product
                for i, row in df.iterrows():
                    groups[f"row_{i+1}"] = pd.DataFrame([row])
    except Exception as e:
        print(f"ERROR during grouping: {e}")
        return 3

    manifest_path = os.path.join(out_dir, 'manifest.csv')
    with open(manifest_path, 'w', newline='', encoding='utf-8') as mf:
        writer = csv.writer(mf)
        writer.writerow(['product_key', 'file', 'status', 'warnings'])

        for product_key, group_df in groups.items():
            # simple validation
            warnings = validate_group(group_df, args.min_images, image_cols)
            status = 'ok' if not warnings else 'warning'
            safe_key = (str(product_key).strip() or 'unnamed').replace(' ', '_')
            filename = safe_key
            try:
                written = write_group(group_df, out_dir, filename, as_xlsx=args.xlsx)
            except Exception as e:
                written = ''
                status = 'error'
                warnings.append(str(e))
            writer.writerow(build_manifest_row(product_key, written, status, warnings))

    print(f"Done. Wrote {len(groups)} product files. Manifest: {manifest_path}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
