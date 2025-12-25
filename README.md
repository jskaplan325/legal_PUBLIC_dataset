# Legal Dataset

Public legal documents for testing and research purposes.

## Data Sources

### 1. Pile of Law (EDGAR Subset)
Curated legal documents from SEC EDGAR filings, organized into simulated "matters" by practice area.

**Location:** `legal_test_matters/`

| Practice Area | Matters | Document Types |
|---------------|---------|----------------|
| M&A | 5 | Merger agreements, stock/asset purchase agreements |
| Funds | 5 | Investment advisory, LPA, subscription, custody agreements |
| LevFin | 5 | Credit agreements, term loans, security agreements |

### 2. SEC EDGAR Direct
Recent filings downloaded directly from SEC EDGAR for major PE firms.

**Location:** `sec_filings_clean/`

| Ticker | Company |
|--------|---------|
| KKR | KKR & Co. |
| BX | Blackstone |
| APO | Apollo |
| CG | The Carlyle Group |
| ARES | Ares Management |

Filing types: 8-K (material agreements), 10-K (annual reports)

## Scripts

- `download_legal_docs.py` - Download from Pile of Law dataset
- `download_sec_filings.py` - Download from SEC EDGAR
- `process_sec_filings.py` - Convert SEC HTML filings to clean text

## Requirements

```bash
pip install datasets<3.0.0 sec-edgar-downloader
```

## Usage

```bash
# Download from Pile of Law
python download_legal_docs.py

# Download from SEC EDGAR
python download_sec_filings.py
python process_sec_filings.py
```

## License

All source documents are public records from SEC EDGAR.
