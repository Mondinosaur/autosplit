"""Command-line interface for AutoSplit."""
from __future__ import annotations
import argparse
import csv
import os
import sys
from typing import List, Optional

try:
    import pandas as pd
except ImportError:
    pd = None

from . import readers, processors, writers, validators

def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the AutoSplit CLI.
    
    Args:
        argv: Command-line arguments (uses sys.argv if None)
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    # Debug info
    print("\nStarting AutoSplit CLI...")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Command arguments: {argv if argv is not None else sys.argv[1:]}")
    
    try:
        import pandas as pd
        print(f"Pandas version: {pd.__version__}")
    except ImportError:
        print("Warning: pandas not found")
    
    # Directory checks
    print("\nDirectory checks:")
    for d in ['inputs', 'outputs']:
        exists = os.path.exists(d)
        writable = os.access(d, os.W_OK) if exists else False
        print(f"{d}/: exists={exists}, writable={writable}")
    parser = argparse.ArgumentParser(
        prog='autosplit', 
        description='Split multi-product sheets into per-product files'
    )
    parser.add_argument('input', help='Input .xlsx or .csv file (or a folder)')
    parser.add_argument('--key-col', help='Column name to group by (e.g. SKU)')
    parser.add_argument('--block', action='store_true', 
                       help='Split by blank-row blocks instead of a key column')
    parser.add_argument('--sheet', default=None, help='Sheet name or index (for xlsx)')
    parser.add_argument('--min-images', type=int, default=0, 
                       help='Minimum number of image URLs expected')
    parser.add_argument('--image-cols', help='Comma-separated list of image columns to check')
    parser.add_argument('--keep-empty-cols', action='store_true')
    parser.add_argument('--xlsx', action='store_true', help='Write output XLSX (default)')
    parser.add_argument('--output-dir', default='outputs', 
                       help='Directory to write outputs')

    args = parser.parse_args(argv)
    
    # Convert output_dir to absolute path if it's not already
    out_dir = os.path.abspath(args.output_dir)
    print(f"\nUsing output directory: {out_dir}")
    
    writers.ensure_dir(out_dir)
    print(f"Output directory exists: {os.path.exists(out_dir)}")
    print(f"Output directory is writable: {os.access(out_dir, os.W_OK)}")
    
    image_cols = args.image_cols.split(',') if args.image_cols else None

    # Read input file
    try:
        df = readers.read_input(args.input, sheet=args.sheet)
    except Exception as e:
        print(f"ERROR: failed to read input '{args.input}': {e}")
        return 2

    if df is None or df.empty:
        print("No rows found in input file.")
        return 1

    # Split into groups
    groups = {}
    try:
        if args.key_col:
            groups = processors.split_by_key(df, args.key_col)
        elif args.block:
            groups = processors.split_by_blocks(df)
        else:
            try:
                key_col = processors.get_default_key_column(df)
                groups = processors.split_by_key(df, key_col)
            except ValueError:
                # fallback: treat each row as a product
                for i, row in df.iterrows():
                    groups[f"row_{i+1}"] = pd.DataFrame([row])
    except Exception as e:
        print(f"ERROR during grouping: {e}")
        return 3

    # Write output files and manifest
    manifest_path = os.path.join(out_dir, 'manifest.csv')
    print(f"\nAttempting to write manifest to: {manifest_path}")
    print(f"Output directory exists: {os.path.exists(out_dir)}")
    print(f"Output directory is writable: {os.access(out_dir, os.W_OK)}")
    
    try:
        with open(manifest_path, 'w', newline='', encoding='utf-8') as mf:
            print(f"Successfully opened {manifest_path} for writing")
            writer = csv.writer(mf)
            writer.writerow(['product_key', 'file', 'status', 'warnings'])
    except IOError as e:
        print(f"Error writing manifest: {e}")
        return 1
        writer = csv.writer(mf)
        writer.writerow(['product_key', 'file', 'status', 'warnings'])

        for product_key, group_df in groups.items():
            warnings = validators.validate_group(
                group_df, 
                args.min_images, 
                image_cols
            )
            status = 'ok' if not warnings else 'warning'
            safe_key = (str(product_key).strip() or 'unnamed').replace(' ', '_')
            
            try:
                written = writers.write_group(
                    group_df, 
                    out_dir, 
                    safe_key, 
                    as_xlsx=args.xlsx
                )
            except Exception as e:
                written = ''
                status = 'error'
                warnings.append(str(e))
                
            writer.writerow(
                writers.build_manifest_row(product_key, written, status, warnings)
            )

    print(f"Done. Wrote {len(groups)} product files. Manifest: {manifest_path}")
    return 0