# Legal PUBLIC Dataset

Public legal documents for testing and research purposes.

## Matter Naming Convention

All matters follow a standardized naming format:

```
[CLIENT_ID]-[MATTER_ID]_[PRACTICE_AREA]_[DESCRIPTION]
```

**Examples:**
- `12001-00001_IFG_Blackstone_Credit_Fund`
- `14001-00003_LevFin`
- `15001-00002_MandA`

| Component | Description |
|-----------|-------------|
| CLIENT_ID | 5-digit client identifier |
| MATTER_ID | 5-digit matter number (unique per client) |
| PRACTICE_AREA | Practice group abbreviation (IFG, LevFin, MandA, etc.) |
| DESCRIPTION | Optional descriptive name |

## Practice Areas

| Code | Practice Area | Client Range |
|------|---------------|--------------|
| IFG | Investment Fund Group | 12xxx, 13xxx |
| LevFin | Leveraged Finance | 14xxx |
| MandA | Mergers & Acquisitions | 15xxx |

## Data Structure

### Test Matters

**Location:** `legal_test_matters/`

| Practice Area | Matter Numbers | Count | Document Types |
|---------------|----------------|-------|----------------|
| Investment Fund Group | 12001-12003, 13000-13001 | 9 | LOAs, LPAs, Subscription Agreements, Side Letters, IMAs |
| Leveraged Finance | 14001-00001 to 14001-00005 | 5 | Credit Agreements, Term Loans, Security Agreements |
| M&A | 15001-00001 to 15001-00005 | 5 | Merger Agreements, Stock/Asset Purchase Agreements |
| Mixed/Legacy | 10234-11456 | 10 | Various SEC filings |

### Document Formats

- **PDF** - Letters of Authorization, Subscription Agreements
- **DOCX** - LPAs, Side Letters, Investment Management Agreements
- **TXT** - Extracted/processed documents from SEC filings

## Data Sources

### 1. Investment Fund Documents
Realistic fund formation documents including:
- Letters of Authorization (Custodian, Wire Transfer, Administrator)
- Limited Partnership Agreements
- Subscription Agreements
- Side Letters
- Investment Management Agreements

### 2. Pile of Law (EDGAR Subset)
Curated legal documents from SEC EDGAR filings.

### 3. SEC EDGAR Direct
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

## Adding New Matters

When adding new matters, always use the naming convention:

1. Determine the practice area and client ID range
2. Assign the next available matter number
3. Create folder: `[CLIENT_ID]-[MATTER_ID]_[PRACTICE_AREA]_[Description]`
4. Add documents in appropriate formats (PDF, DOCX, TXT)

## License

All source documents are public records from SEC EDGAR or synthetically generated for testing purposes.
