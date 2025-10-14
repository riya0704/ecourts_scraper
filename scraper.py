#!/usr/bin/env python3
"""
scraper.py

eCourts Scraper - CLI tool for checking court case listings

Features:
- Input CNR OR Case Type + Number + Year
- Check if listed today or tomorrow
- If listed, print serial number and court name
- Optionally download case PDF (if available)
- Optionally download entire cause list for a date
- Save results as JSON files
- Simple Flask API wrapper available

Usage examples:
    # Check case by CNR for today
    python scraper.py --cnr "MHMU01234567890123" --today
    
    # Check case by type/number/year for tomorrow
    python scraper.py --type "CR" --number 123 --year 2024 --tomorrow
    
    # Download cause list for today
    python scraper.py --causelist --today --download-pdf
    
    # Check case for specific date
    python scraper.py --cnr "MHMU01234567890123" --date "2024-10-20"

Author: Intern Task - eCourts Scraper
Deadline: 20th October 2024
"""

import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
import re
from urllib.parse import urljoin

# Output folders
OUT_DIR = "outputs"
CAUSE_DIR = os.path.join(OUT_DIR, "causelists")
CASE_DIR = os.path.join(OUT_DIR, "cases")
os.makedirs(CAUSE_DIR, exist_ok=True)
os.makedirs(CASE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# eCourts specific URLs and tokens
ECOURTS_BASE = "https://services.ecourts.gov.in/ecourtindia_v6/"
ECOURTS_URLS = {
    "home": "https://services.ecourts.gov.in/ecourtindia_v6/?p=home/index&app_token=2829a7e11a857da6b646dab029a6c38d1dfe692e9ee9e4d0945d2ba65e03def1",
    "cause_list": "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/index&app_token=7970d9011f0e6dc03b8549c7b2c9fae2c22b543bb6e33d6e43686becea3434e3",
    "caveat_search": "https://services.ecourts.gov.in/ecourtindia_v6/?p=caveat_search/index&app_token=97b347aea82a6db3056087cd5a0ae943461b868f21c7fc51daa650ed70e3e0ca"
}

# Regex for basic CNR detection (very permissive)
CNR_RE = re.compile(r"[A-Za-z0-9\-\/]{8,}")

def date_for(flag_today, flag_tomorrow, explicit_date):
    if explicit_date:
        return datetime.strptime(explicit_date, "%Y-%m-%d").date()
    if flag_tomorrow:
        return (datetime.now().date() + timedelta(days=1))
    return datetime.now().date()

def create_session():
    """Create a requests session with proper headers for eCourts"""
    session = requests.Session()
    session.headers.update(HEADERS)
    return session

def try_download(url, dest_path):
    """Download a URL to dest_path. Returns True on success."""
    try:
        session = create_session()
        r = session.get(url, timeout=30, stream=True)
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(1024*8):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"[!] Download failed: {e} -- {url}")
        return False

def search_ecourts_cause_list(session, case_identifier, check_date):
    """
    Search eCourts cause list using the actual website interface
    """
    date_str_ddmmyyyy = check_date.strftime("%d-%m-%Y")
    results = {"found": False, "serial_number": None, "court_name": None, "case_pdf": None, "matched_line": None}
    
    try:
        # First, visit the cause list page to get the form
        print(f"[INFO] Accessing eCourts cause list page...")
        response = session.get(ECOURTS_URLS["cause_list"], timeout=20)
        
        if response.status_code != 200:
            print(f"[WARNING] Could not access cause list page: {response.status_code}")
            return results
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Look for the cause list form
        forms = soup.find_all("form")
        if forms:
            print(f"[INFO] Found {len(forms)} forms on the page")
            
            # Analyze the main form
            main_form = forms[0]  # Usually the first form is the main one
            
            # Check if the form has the expected fields
            date_field = main_form.find("input", {"name": "causelist_date"})
            court_field = main_form.find("select", {"name": "CL_court_no"})
            captcha_field = main_form.find("input", {"name": "cause_list_captcha_code"})
            
            if date_field:
                current_date = date_field.get('value', '')
                print(f"[INFO] Form date field found with value: {current_date}")
                
                # Check if the date matches our search date
                if current_date == date_str_ddmmyyyy:
                    print(f"[INFO] Date matches our search date: {date_str_ddmmyyyy}")
                else:
                    print(f"[INFO] Form date ({current_date}) differs from search date ({date_str_ddmmyyyy})")
            
            if court_field:
                options = court_field.find_all("option")
                print(f"[INFO] Court selection dropdown found with {len(options)} options")
                
                # List available courts
                for opt in options[:5]:  # Show first 5 courts
                    value = opt.get('value', '')
                    text = opt.get_text().strip()
                    if value and text != "Select court":
                        print(f"[INFO] Available court: {value} - {text}")
            
            if captcha_field:
                print(f"[WARNING] CAPTCHA field detected - automated submission not possible")
                print(f"[INFO] Manual intervention would be required for form submission")
        
        # Search for any content that might contain case information in the current page
        page_text = soup.get_text(separator=" ", strip=True)
        
        # If case identifier is provided, search for it in the page content
        if case_identifier and case_identifier.upper() in page_text.upper():
            print(f"[SUCCESS] Found case identifier '{case_identifier}' in page content!")
            
            # Try to extract context around the match
            lines = page_text.split('\n')
            for i, line in enumerate(lines):
                if case_identifier.upper() in line.upper():
                    results["found"] = True
                    results["matched_line"] = line.strip()
                    
                    # Try to extract serial number (look for numbers at start of line)
                    serial_match = re.search(r'^\s*(\d+)[\.\s]', line)
                    if serial_match:
                        results["serial_number"] = serial_match.group(1)
                    
                    # Try to find court name in nearby content
                    context_start = max(0, i-5)
                    context_end = min(len(lines), i+5)
                    context = ' '.join(lines[context_start:context_end])
                    
                    court_patterns = [
                        r'(District Court[^,\n]*)',
                        r'(High Court[^,\n]*)',
                        r'(Sessions Court[^,\n]*)',
                        r'(Magistrate Court[^,\n]*)'
                    ]
                    
                    for pattern in court_patterns:
                        court_match = re.search(pattern, context, re.IGNORECASE)
                        if court_match:
                            results["court_name"] = court_match.group(1).strip()
                            break
                    
                    break
        
        # Look for PDF links
        pdf_links = soup.find_all("a", href=re.compile(r'\.pdf$', re.IGNORECASE))
        if pdf_links:
            print(f"[INFO] Found {len(pdf_links)} PDF links on the page")
            # Take the first PDF link found
            pdf_href = pdf_links[0].get('href')
            if pdf_href:
                if pdf_href.startswith('http'):
                    results["case_pdf"] = pdf_href
                else:
                    results["case_pdf"] = urljoin(response.url, pdf_href)
                print(f"[INFO] PDF link: {results['case_pdf']}")
        
        # Additional information about the page structure
        print(f"[INFO] Page analysis complete - CAPTCHA protection detected")
        print(f"[INFO] For real case searches, manual form submission would be required")
        
    except Exception as e:
        print(f"[WARNING] Error searching eCourts: {e}")
    
    return results

def search_cause_list_for_case(case_identifier, check_date):
    """
    Try multiple strategies to find case in cause list of a given date.
    Returns dict with keys: found(bool), serial_number, court_name, case_pdf (optional)
    """
    date_str_ddmmyyyy = check_date.strftime("%d-%m-%Y")
    date_str_yyyy_mm_dd = check_date.strftime("%Y-%m-%d")
    date_str_ddmmyy = check_date.strftime("%d-%m-%y")
    results = {"found": False, "serial_number": None, "court_name": None, "case_pdf": None, "matched_line": None}

    # Strategy 1: Use actual eCourts URLs with app tokens
    # Updated with real URLs from the eCourts system
    possible_urls = [
        # Main cause list page with app token
        f"https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/index&app_token=7970d9011f0e6dc03b8549c7b2c9fae2c22b543bb6e33d6e43686becea3434e3",
        
        # Try with date parameters
        f"https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/index&app_token=7970d9011f0e6dc03b8549c7b2c9fae2c22b543bb6e33d6e43686becea3434e3&date={date_str_ddmmyyyy}",
        f"https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/index&app_token=7970d9011f0e6dc03b8549c7b2c9fae2c22b543bb6e33d6e43686becea3434e3&date={date_str_yyyy_mm_dd}",
        
        # Legacy URL patterns (fallback)
        f"https://services.ecourts.gov.in/ecourtindia_v6/causeList?date={date_str_ddmmyyyy}",
        f"https://services.ecourts.gov.in/ecourtindia_v6/causeList?date={date_str_yyyy_mm_dd}",
        f"https://services.ecourts.gov.in/ecourtindia_v6/causelistpdf?date={date_str_ddmmyyyy}",
        f"https://services.ecourts.gov.in/ecourtindia_v6/causelistpdf?date={date_str_yyyy_mm_dd}"
    ]

    # Add home page URL for reference
    home_url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=home/index&app_token=2829a7e11a857da6b646dab029a6c38d1dfe692e9ee9e4d0945d2ba65e03def1"
    possible_urls.append(home_url)

    # Strategy 1: Use the new eCourts-specific search
    session = create_session()
    ecourts_results = search_ecourts_cause_list(session, case_identifier, check_date)
    if ecourts_results.get("found"):
        return ecourts_results

    # Strategy 2: Try fetching each possible URL and parsing HTML for case identifier
    for url in possible_urls:
        try:
            r = session.get(url, timeout=20)
            if r.status_code != 200:
                continue
            html = r.text
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            if case_identifier and (case_identifier in text or re.search(re.escape(case_identifier), text, re.IGNORECASE)):
                # crude search: find lines that contain the identifier
                for tag in soup.find_all(text=re.compile(re.escape(case_identifier), re.IGNORECASE)):
                    parent = tag.parent
                    line = parent.get_text(" ", strip=True)
                    # Attempt to extract serial number (e.g., starts with number) and court name
                    # Heuristics:
                    serial_match = re.search(r"\bSerial[:\s]*([0-9]+)\b", line, re.IGNORECASE) or re.search(r"^\s*([0-9]{1,3})\b", line)
                    serial = serial_match.group(1) if serial_match else None
                    court = None
                    # look for a nearby <h2> or <h3> for court name
                    court_tag = soup.find(["h1","h2","h3","strong"])
                    if court_tag:
                        court = court_tag.get_text(" ", strip=True)
                    results.update({"found": True, "serial_number": serial, "court_name": court, "matched_line": line})
                    # try to find a PDF link in the page near the match
                    for a in parent.find_all_next("a", href=True, limit=6):
                        href = a['href']
                        if href.lower().endswith(".pdf"):
                            pdf_url = urljoin(r.url, href)
                            results["case_pdf"] = pdf_url
                            break
                    if results["found"]:
                        return results
        except Exception as e:
            # ignore and try next
            # print(f"[!] Error trying {url}: {e}")
            continue

    # Strategy 3: Try known cause list PDF naming conventions with updated paths
    pdf_name_candidates = [
        f"causelist_{date_str_yyyy_mm_dd}.pdf",
        f"CauseList_{date_str_yyyy_mm_dd}.pdf",
        f"CauseList_{date_str_ddmmyyyy}.pdf",
        f"causelist_{date_str_ddmmyy}.pdf",
        f"daily_causelist_{date_str_ddmmyyyy}.pdf"
    ]
    base_attempts = [
        "https://services.ecourts.gov.in/ecourtindia_v6/static_causes/",
        "https://services.ecourts.gov.in/ecourtindia_v6/causelists/",
        "https://services.ecourts.gov.in/ecourtindia_v6/uploads/causelists/",
        "https://services.ecourts.gov.in/ecourtindia_v6/pdfs/",
        "https://services.ecourts.gov.in/ecourtindia_v6/documents/"
    ]
    for base in base_attempts:
        for name in pdf_name_candidates:
            pdf_url = base + name
            try:
                head = session.head(pdf_url, timeout=10)
                if head.status_code == 200 and 'application/pdf' in head.headers.get('Content-Type',''):
                    results.update({"found": False, "case_pdf": pdf_url})
                    print(f"[INFO] Found potential cause list PDF: {pdf_url}")
                    return results
            except Exception:
                continue

    return results

def download_and_search_pdf(pdf_url, case_identifier, dest_folder):
    """
    Download a PDF to dest_folder and try to search for the case_identifier inside.
    NOTE: PDF text extraction is not implemented in this script to keep dependencies small.
    If you want to search inside PDF, install pdfminer.six and implement extraction.
    For now this function downloads the PDF and returns the path.
    """
    fname = os.path.basename(pdf_url.split("?")[0]) or f"causelist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    dest = os.path.join(dest_folder, fname)
    ok = try_download(pdf_url, dest)
    return dest if ok else None

def save_json(result_obj, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result_obj, f, indent=2, ensure_ascii=False)

def main():
    parser = argparse.ArgumentParser(
        description="eCourts cause list / case checker (best-effort)",
        epilog="""
Examples:
  %(prog)s --cnr "MHMU01234567890123" --today
  %(prog)s --type "CR" --number 123 --year 2024 --tomorrow  
  %(prog)s --causelist --today --download-pdf
  %(prog)s --cnr "DLCT01234567890123" --date "2024-10-20"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Case identification group
    case_group = parser.add_argument_group('Case Identification')
    case_group.add_argument("--cnr", help="Full CNR string (e.g., MHMU01234567890123)")
    case_group.add_argument("--type", help="Case type (e.g., CR, CIV, FA, CC)")
    case_group.add_argument("--number", type=int, help="Case number")
    case_group.add_argument("--year", type=int, help="Case year")
    
    # Date selection group
    date_group = parser.add_argument_group('Date Selection')
    date_group.add_argument("--date", help="Explicit date YYYY-MM-DD (overrides --today/--tomorrow)")
    date_group.add_argument("--today", action="store_true", help="Check for today's date")
    date_group.add_argument("--tomorrow", action="store_true", help="Check for tomorrow's date")
    
    # Action group
    action_group = parser.add_argument_group('Actions')
    action_group.add_argument("--causelist", action="store_true", help="Download entire cause list for the date")
    action_group.add_argument("--download-pdf", action="store_true", help="Download any found PDFs (case or cause list)")
    
    args = parser.parse_args()

    # Validation
    if not (args.cnr or (args.type and args.number and args.year) or args.causelist):
        print("[ERROR] Please provide either:")
        print("   • --cnr <CNR_NUMBER>")
        print("   • --type <TYPE> --number <NUM> --year <YEAR>")
        print("   • --causelist (to download cause list)")
        print("\nUse --help for more details and examples.")
        return 1
    
    # Validate CNR format if provided
    if args.cnr and not CNR_RE.match(args.cnr):
        print(f"[WARNING] CNR '{args.cnr}' doesn't match expected format")
        print("   Expected format: 16-character alphanumeric (e.g., MHMU01234567890123)")
    
    # Validate year if provided
    if args.year and (args.year < 1950 or args.year > datetime.now().year + 1):
        print(f"[ERROR] Invalid year {args.year}. Must be between 1950 and {datetime.now().year + 1}")
        return 1

    # Build case identifier string
    case_identifier = None
    if args.cnr:
        case_identifier = args.cnr.strip()
    elif args.type and args.number and args.year:
        case_identifier = f"{args.type.strip()} {args.number} / {args.year}"

    # Determine date with validation
    try:
        check_date = date_for(args.today, args.tomorrow, args.date)
    except ValueError as e:
        print(f"❌ Error: Invalid date format. Use YYYY-MM-DD (e.g., 2024-10-20)")
        return 1
    
    # Create safe filename
    safe_identifier = (case_identifier or 'causelist').replace(' ', '_').replace('/', '_')
    output_filename = os.path.join(OUT_DIR, f"result_{safe_identifier}_{check_date}.json")
    
    print(f"[INFO] Searching for: {case_identifier or 'cause list'}")
    print(f"[INFO] Date: {check_date}")
    print(f"[INFO] Output will be saved to: {output_filename}")
    print("-" * 50)

    # If causelist requested: try to find cause list PDF and download
    if args.causelist:
        print("[INFO] Searching for cause list...")
        res = search_cause_list_for_case("", check_date)
        out = {
            "query": {"causelist_for": str(check_date), "timestamp": datetime.now().isoformat()}, 
            "found_causelist_pdf": False, 
            "causelist_pdf": None
        }
        
        if res.get("case_pdf"):
            print(f"[SUCCESS] Found cause-list PDF link: {res['case_pdf']}")
            out["found_causelist_pdf"] = True
            out["causelist_pdf"] = res["case_pdf"]
            
            if args.download_pdf:
                print("[INFO] Downloading cause list PDF...")
                saved = download_and_search_pdf(res["case_pdf"], "", CAUSE_DIR)
                if saved:
                    print(f"[SUCCESS] Saved cause list to: {saved}")
                    out["saved_file"] = saved
                else:
                    print("[ERROR] Failed to download cause list PDF")
        else:
            print("[ERROR] No direct cause-list PDF link discovered automatically.")
            print("   The script attempted multiple heuristics but couldn't find a downloadable cause list.")
            out["note"] = "No direct PDF link discovered automatically. The eCourts website structure may have changed."

        save_json(out, output_filename)
        print(f"[INFO] Saved metadata to {output_filename}")
        return 0

    # For case lookup:
    print("[INFO] Searching for case in cause lists...")
    res_today = search_cause_list_for_case(case_identifier, check_date)
    out = {
        "query": {
            "case_identifier": case_identifier, 
            "date_checked": str(check_date),
            "timestamp": datetime.now().isoformat()
        }, 
        "listed": False
    }
    
    if res_today.get("found"):
        out.update({
            "listed": True,
            "serial_number": res_today.get("serial_number"),
            "court_name": res_today.get("court_name"),
            "matched_line": res_today.get("matched_line")
        })
        print(f"[SUCCESS] Case found and listed on {check_date}!")
        print(f"   Serial number: {out.get('serial_number') or 'Not found'}")
        print(f"   Court name: {out.get('court_name') or 'Not found'}")
        if out.get('matched_line'):
            print(f"   Matched text: {out.get('matched_line')[:100]}...")
            
        if res_today.get("case_pdf"):
            out["case_pdf_link"] = res_today.get("case_pdf")
            print(f"   Case PDF link: {res_today.get('case_pdf')}")
            if args.download_pdf:
                print("[INFO] Downloading case PDF...")
                saved = download_and_search_pdf(res_today.get("case_pdf"), case_identifier, CASE_DIR)
                if saved:
                    print(f"[SUCCESS] Saved case PDF to {saved}")
                    out["case_pdf_saved"] = saved
                else:
                    print("[ERROR] Failed to download case PDF")
    else:
        print(f"[NOT FOUND] Case not found in cause list for {check_date}")
        print("   This could mean:")
        print("   • Case is not listed on this date")
        print("   • eCourts website structure has changed")
        print("   • Case identifier format is incorrect")
        out["note"] = "Case not found with current heuristics. The eCourts website may have changed or case may not be listed."

    save_json(out, output_filename)
    print(f"[INFO] Saved result to {output_filename}")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
