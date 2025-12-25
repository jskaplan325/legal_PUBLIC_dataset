import os
from datasets import load_dataset

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
output_path = "./legal_test_matters"
os.makedirs(output_path, exist_ok=True)

TARGET_MATTERS_PER_TYPE = 5  # Creates M_and_A_1, M_and_A_2, ... M_and_A_5
MIN_DOC_LENGTH = 15000  # Skip short docs

# ---------------------------------------------------------
# PRACTICE AREAS: "HERO" DOCUMENTS
# ---------------------------------------------------------
PRACTICE_AREAS = {
    "M_and_A": [
        "agreement and plan of merger",
        "asset purchase agreement",
        "stock purchase agreement"
    ],
    "Funds": [
        "investment advisory agreement",
        "investment management agreement",
        "limited partnership agreement",
        "subscription agreement",
        "administration agreement",
        "custody agreement"
    ],
    "LevFin": [
        "credit agreement",
        "term loan agreement",
        "guarantee and collateral agreement",
        "security agreement"
    ]
}

# Track what we've collected
matter_counts = {"M_and_A": 0, "Funds": 0, "LevFin": 0}

# Track documents per matter (to add variety within each "fake matter")
matter_docs = {
    "M_and_A": {},   # {1: [doc1, doc2], 2: [doc1], ...}
    "Funds": {},
    "LevFin": {}
}

DOCS_PER_MATTER = 10  # Try to get ~10 docs per fake matter

def classify_document(text):
    """
    Classify a single document by practice area.
    Returns (practice_area, hero_type) or (None, None)
    """
    if len(text) < MIN_DOC_LENGTH:
        return None, None

    header = text[:5000].lower()

    # Check Funds first (need BDC/partnership context)
    for hero in PRACTICE_AREAS["Funds"]:
        if hero in header:
            if any(kw in header for kw in ["business development company", "investment company act", "partnership", "fund", "limited partner"]):
                return "Funds", hero

    # Check LevFin
    for hero in PRACTICE_AREAS["LevFin"]:
        if hero in header:
            return "LevFin", hero

    # Check M&A
    for hero in PRACTICE_AREAS["M_and_A"]:
        if hero in header:
            return "M_and_A", hero

    return None, None

def get_smart_filename(text, hero_type, doc_index):
    """Generate a descriptive filename."""
    header = text[:2000].lower()

    # Hero document names
    hero_names = {
        "agreement and plan of merger": "HERO_Merger_Agreement",
        "asset purchase agreement": "HERO_Asset_Purchase_Agreement",
        "stock purchase agreement": "HERO_Stock_Purchase_Agreement",
        "investment advisory agreement": "HERO_Investment_Advisory_Agreement",
        "investment management agreement": "HERO_Investment_Management_Agreement",
        "limited partnership agreement": "HERO_LPA",
        "subscription agreement": "HERO_Subscription_Agreement",
        "administration agreement": "HERO_Administration_Agreement",
        "custody agreement": "HERO_Custody_Agreement",
        "credit agreement": "HERO_Credit_Agreement",
        "term loan agreement": "HERO_Term_Loan_Agreement",
        "guarantee and collateral agreement": "HERO_Guarantee_Collateral",
        "security agreement": "HERO_Security_Agreement"
    }

    if hero_type in hero_names:
        return f"{hero_names[hero_type]}.txt"

    # Ancillary document detection
    if "voting agreement" in header:
        return f"Ancillary_Voting_Agreement_{doc_index}.txt"
    if "support agreement" in header:
        return f"Ancillary_Support_Agreement_{doc_index}.txt"
    if "opinion" in header:
        return f"Ancillary_Legal_Opinion_{doc_index}.txt"
    if "disclosure" in header:
        return f"Ancillary_Disclosure_Schedule_{doc_index}.txt"
    if "exhibit" in header:
        return f"Ancillary_Exhibit_{doc_index}.txt"

    return f"Document_{doc_index}.txt"

def save_matter(practice_area, matter_num, docs):
    """Save all documents for a matter to its folder."""
    folder_name = f"{practice_area}_{matter_num}"
    save_path = os.path.join(output_path, folder_name)
    os.makedirs(save_path, exist_ok=True)

    print(f"\n--- Saving {folder_name} ({len(docs)} docs) ---")

    for i, (text, hero_type) in enumerate(docs):
        filename = get_smart_filename(text, hero_type, i)
        filepath = os.path.join(save_path, filename)

        # Handle duplicate filenames
        if os.path.exists(filepath):
            base, ext = os.path.splitext(filename)
            filename = f"{base}_{i}{ext}"
            filepath = os.path.join(save_path, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

        marker = "[HERO]" if "HERO" in filename else "[ancillary]"
        print(f"    {marker} {filename}")

# ---------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------
print("Downloading Pile of Law (EDGAR Subset)...")
ds = load_dataset("pile-of-law/pile-of-law", "edgar", split="train", streaming=True, trust_remote_code=True)

print(f"Scanning for documents... Target: {TARGET_MATTERS_PER_TYPE} matters per practice area\n")

docs_processed = 0
for doc in ds:
    docs_processed += 1

    if docs_processed % 2000 == 0:
        print(f"[Progress] {docs_processed} docs scanned | M&A: {matter_counts['M_and_A']}, Funds: {matter_counts['Funds']}, LevFin: {matter_counts['LevFin']}")

    practice_area, hero_type = classify_document(doc['text'])

    if practice_area and matter_counts[practice_area] < TARGET_MATTERS_PER_TYPE:
        # Determine which matter number to add this to
        current_matter = matter_counts[practice_area] + 1

        # Initialize matter if needed
        if current_matter not in matter_docs[practice_area]:
            matter_docs[practice_area][current_matter] = []

        # Add doc to current matter
        matter_docs[practice_area][current_matter].append((doc['text'], hero_type))

        snippet = doc['text'][:50].replace('\n', ' ')
        print(f"[Found {practice_area}_{current_matter}] {hero_type}: {snippet}...")

        # If we have enough docs for this matter, finalize it and move to next
        if len(matter_docs[practice_area][current_matter]) >= DOCS_PER_MATTER:
            save_matter(practice_area, current_matter, matter_docs[practice_area][current_matter])
            matter_counts[practice_area] += 1

    # Check if done
    if all(c >= TARGET_MATTERS_PER_TYPE for c in matter_counts.values()):
        print("\n*** All Test Sets Collected! ***")
        break

# Save any partially-filled matters at the end
print("\n--- Saving remaining partial matters ---")
for practice_area in matter_docs:
    for matter_num, docs in matter_docs[practice_area].items():
        if docs and matter_num > matter_counts[practice_area]:
            save_matter(practice_area, matter_num, docs)
            matter_counts[practice_area] = matter_num

# Summary
print(f"\n{'='*50}")
print("DATASET GENERATION COMPLETE")
print(f"{'='*50}")
print(f"Documents scanned: {docs_processed}")
print(f"M&A Matters: {matter_counts['M_and_A']}")
print(f"Funds Matters: {matter_counts['Funds']}")
print(f"LevFin Matters: {matter_counts['LevFin']}")
print(f"\nSaved to: {output_path}/")
