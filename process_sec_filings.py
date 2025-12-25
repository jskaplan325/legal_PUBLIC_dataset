import os
import re
from pathlib import Path

raw_dir = Path("./sec_filings_raw/sec-edgar-filings")
output_dir = Path("./sec_filings_clean")

def clean_sec_text(content):
    """Clean SEC filing text - remove HTML tags and clean up."""
    # Remove SGML/XML headers
    content = re.sub(r'<SEC-HEADER>.*?</SEC-HEADER>', '', content, flags=re.DOTALL)
    content = re.sub(r'<IMS-HEADER>.*?</IMS-HEADER>', '', content, flags=re.DOTALL)

    # Remove XML declarations
    content = re.sub(r'<\?xml[^>]*\?>', '', content)

    # Remove script and style
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

    # Replace common entities
    content = content.replace('&nbsp;', ' ')
    content = content.replace('&amp;', '&')
    content = content.replace('&lt;', '<')
    content = content.replace('&gt;', '>')
    content = content.replace('&quot;', '"')
    content = content.replace('&#39;', "'")
    content = re.sub(r'&#\d+;', ' ', content)

    # Add line breaks for block elements
    content = re.sub(r'<br\s*/?>', '\n', content, flags=re.IGNORECASE)
    content = re.sub(r'</p>', '\n\n', content, flags=re.IGNORECASE)
    content = re.sub(r'</div>', '\n', content, flags=re.IGNORECASE)
    content = re.sub(r'</tr>', '\n', content, flags=re.IGNORECASE)
    content = re.sub(r'</td>', '\t', content, flags=re.IGNORECASE)
    content = re.sub(r'</li>', '\n', content, flags=re.IGNORECASE)

    # Remove all HTML tags
    content = re.sub(r'<[^>]+>', '', content)

    # Clean up excessive whitespace
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    content = re.sub(r'[ \t]+', ' ', content)
    content = re.sub(r' +\n', '\n', content)

    return content.strip()

def extract_exhibits(content):
    """Try to find and extract exhibit documents from the filing."""
    exhibits = {}

    # Look for DOCUMENT sections
    doc_pattern = r'<DOCUMENT>(.*?)</DOCUMENT>'
    documents = re.findall(doc_pattern, content, re.DOTALL)

    for i, doc in enumerate(documents):
        # Try to get document type
        type_match = re.search(r'<TYPE>([^\n<]+)', doc)
        filename_match = re.search(r'<FILENAME>([^\n<]+)', doc)

        doc_type = type_match.group(1).strip() if type_match else f"doc_{i}"
        filename = filename_match.group(1).strip() if filename_match else f"document_{i}.txt"

        # Clean the document content
        cleaned = clean_sec_text(doc)

        if len(cleaned) > 2000:  # Only keep substantial docs
            safe_name = re.sub(r'[^\w\-.]', '_', filename)
            exhibits[f"{doc_type}_{safe_name}"] = cleaned

    return exhibits

print("Processing SEC filings...\n")

for ticker_dir in raw_dir.iterdir():
    if not ticker_dir.is_dir():
        continue

    ticker = ticker_dir.name
    print(f"\n{ticker}")
    print("=" * 40)

    for form_dir in ticker_dir.iterdir():
        if not form_dir.is_dir():
            continue

        form_type = form_dir.name

        for filing_dir in form_dir.iterdir():
            if not filing_dir.is_dir():
                continue

            accession = filing_dir.name
            submission_file = filing_dir / "full-submission.txt"

            if not submission_file.exists():
                continue

            print(f"  {form_type}/{accession}:")

            # Read the submission
            with open(submission_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Create output directory
            out_path = output_dir / ticker / f"{form_type}_{accession}"
            out_path.mkdir(parents=True, exist_ok=True)

            # Extract exhibits
            exhibits = extract_exhibits(content)

            if exhibits:
                for name, text in exhibits.items():
                    # Truncate long filenames
                    safe_name = name[:80] + ".txt" if len(name) > 80 else name + ".txt"
                    out_file = out_path / safe_name

                    with open(out_file, 'w', encoding='utf-8') as f:
                        f.write(text)

                    size_kb = len(text) / 1024
                    print(f"    + {safe_name[:50]}... ({size_kb:.1f} KB)")
            else:
                # Just save cleaned full submission
                cleaned = clean_sec_text(content)
                out_file = out_path / "full_submission_cleaned.txt"

                with open(out_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned)

                size_kb = len(cleaned) / 1024
                print(f"    + full_submission_cleaned.txt ({size_kb:.1f} KB)")

print(f"\n\n--- COMPLETE ---")
print(f"Output: {output_dir}/")

# Summary
total_files = sum(1 for _ in output_dir.rglob("*.txt"))
total_size = sum(f.stat().st_size for f in output_dir.rglob("*.txt"))
print(f"Total files: {total_files}")
print(f"Total size: {total_size / (1024*1024):.1f} MB")
