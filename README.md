# AutoSplit — Multi-Product Sheet Splitter (scaffold)

Quick scaffold for the AutoSplit tool. It reads a multi-product XLSX/CSV and writes one output file per product plus a `manifest.csv`.

Requirements
- Python 3.10+
- Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Quick start
1. Put an input file in `inputs/` (example provided: `inputs/example_products.csv`).
2. Run the scaffold:

```bash
python3 autosplit.py inputs/example_products.csv --key-col SKU --min-images 1 --xlsx
```

Outputs
- Per-product files go to `outputs/`.
- `outputs/manifest.csv` contains columns: product_key,file,status,warnings

Notes
- This is a scaffold: it performs basic grouping and validation. For production use, add tests, edge-case handling, and robust header mapping.

If you'd like, I can:
- Add a VS Code `tasks.json` and `bootstrap.sh` for one-click setup
- Implement fuzzy header mapping and chunked reading for large files
- Add unit tests and a CI workflow
