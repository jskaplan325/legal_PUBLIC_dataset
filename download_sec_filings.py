import os
import re
from sec_edgar_downloader import Downloader
from pathlib import Path

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
dl_identity = "LegalDatasetResearch"
dl_email = "research@legaldataset.com"

# Target tickers - large PE firms with complex filings
targets = [
    "KKR",   # KKR & Co.
    "BX",    # Blackstone
    "APO",   # Apollo
    "CG",    # The Carlyle Group
    "ARES",  # Ares Management
]

download_dir = "./sec_filings_raw"
output_dir = "./sec_filings_txt"

# Initialize Downloader
dl = Downloader(dl_identity, dl_email, download_dir)

def html_to_text(html_content):
    """Simple HTML to text conversion."""
    # Remove script and style elements
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Replace common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")

    # Replace <br> and <p> with newlines
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</tr>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</td>', '\t', text, flags=re.IGNORECASE)

    # Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    text = text.strip()

    return text

def convert_filing_to_txt(filing_path, output_base):
    """Convert all HTML files in a filing folder to TXT."""
    filing_path = Path(filing_path)

    for html_file in filing_path.rglob("*.htm*"):
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()

            text_content = html_to_text(html_content)

            # Skip very short files (likely just headers)
            if len(text_content) < 1000:
                continue

            # Create output path
            relative_path = html_file.relative_to(filing_path)
            output_file = output_base / relative_path.with_suffix('.txt')
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text_content)

            print(f"    Converted: {output_file.name} ({len(text_content):,} chars)")

        except Exception as e:
            print(f"    Error converting {html_file.name}: {e}")

# ---------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------
print(f"--- Starting SEC EDGAR Download ---\n")
os.makedirs(output_dir, exist_ok=True)

for ticker in targets:
    print(f"\nProcessing: {ticker}")
    print("=" * 40)

    # Download 8-K filings (Material Agreements / Deals)
    print(f"  Fetching 8-K filings (deals/agreements)...")
    try:
        dl.get("8-K", ticker, limit=3)
    except Exception as e:
        print(f"    Error: {e}")

    # Download 10-K filings (Annual Reports / Fund Structure)
    print(f"  Fetching 10-K filings (annual reports)...")
    try:
        dl.get("10-K", ticker, limit=1)
    except Exception as e:
        print(f"    Error: {e}")

print("\n\n--- Converting HTML to TXT ---\n")

# Convert all downloaded filings to text
raw_path = Path(download_dir)
output_path = Path(output_dir)

for ticker_dir in raw_path.glob("sec-edgar-filings/*"):
    if ticker_dir.is_dir():
        ticker = ticker_dir.name
        print(f"\nConverting {ticker} filings...")

        for form_dir in ticker_dir.iterdir():
            if form_dir.is_dir():
                form_type = form_dir.name

                for filing_dir in form_dir.iterdir():
                    if filing_dir.is_dir():
                        accession = filing_dir.name
                        output_base = output_path / ticker / form_type / accession
                        print(f"  {form_type}/{accession}:")
                        convert_filing_to_txt(filing_dir, output_base)

print("\n\n--- COMPLETE ---")
print(f"Raw HTML: {download_dir}/")
print(f"Text files: {output_dir}/")
