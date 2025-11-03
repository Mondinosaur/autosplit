# AutoSplit — Multi-Product Sheet Splitter

A Python tool for splitting multi-product spreadsheets into individual files. AutoSplit reads an Excel or CSV file containing multiple products and creates separate files for each product, along with a manifest of the generated files.

## Features

- Supports both Excel (`.xlsx`, `.xls`) and CSV input files
- Multiple splitting strategies:
  - By key column (e.g., SKU, Product ID)
  - By blank-row blocks
  - Row-by-row (fallback)
- Flexible input handling:
  - Multiple CSV encodings and delimiters
  - Multiple Excel sheets
  - Automatic header detection
- Validation of image URLs and other data
- Detailed manifest file with processing status and warnings

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Mondinosaur/autosplit.git
cd autosplit
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

For development, also install development dependencies:
```bash
pip install -r requirements-dev.txt
```

## Usage

### Basic Usage

1. Place your input file in the `inputs/` directory
2. Run AutoSplit:
```bash
python -m autosplit.cli inputs/your_file.xlsx
```

### Command-line Options

- `--key-col COL`: Column name to group by (e.g., SKU)
- `--block`: Split by blank-row blocks instead of a key column
- `--sheet NAME`: Sheet name for Excel files
- `--min-images N`: Minimum number of image URLs expected
- `--image-cols COL1,COL2`: Comma-separated list of image columns
- `--xlsx`: Write output as XLSX files (default)
- `--output-dir DIR`: Output directory (default: outputs/)

### Examples

Split by SKU column:
```bash
python -m autosplit.cli inputs/catalog.xlsx --key-col SKU
```

Split by blank rows:
```bash
python -m autosplit.cli inputs/catalog.xlsx --block
```

Validate image URLs:
```bash
python -m autosplit.cli inputs/catalog.xlsx --min-images 2 --image-cols "Image1,Image2"
```

## Output

The tool creates:
1. One file per product in the `outputs/` directory
2. A `manifest.csv` with columns:
   - `product_key`: Product identifier
   - `file`: Path to output file
   - `status`: Processing status (ok/warning/error)
   - `warnings`: Any validation warnings

## Project Structure

```
autosplit/
├── autosplit/          # Main package
│   ├── __init__.py    # Package initialization
│   ├── cli.py         # Command-line interface
│   ├── readers.py     # Input file handling
│   ├── processors.py  # Data processing
│   ├── writers.py     # Output generation
│   └── validators.py  # Data validation
├── examples/          # Example files
├── inputs/           # Input directory
├── outputs/          # Output directory
├── requirements.txt   # Core dependencies
└── requirements-dev.txt  # Development dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
