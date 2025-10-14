# eCourts Scraper (Intern Task)

A Python-based web scraper for fetching court case listings from the eCourts India portal. This tool helps check if a case is listed for today or tomorrow, and can download case PDFs and cause lists.

## 🎯 Project Goal

Build a Python script to fetch court listings from [eCourts](https://services.ecourts.gov.in/ecourtindia_v6/) with the following capabilities:

1. ✅ Input case details (CNR or Case Type/Number/Year)
2. ✅ Check if case is listed today or tomorrow  
3. ✅ Show serial number and court name if listed
4. ✅ Download case PDFs (if available)
5. ✅ Download entire cause list for today
6. ✅ CLI interface with multiple options
7. ✅ Optional web API interface
8. ✅ Save results as JSON files

**Deadline:** 20th October 2024

## 📁 Project Structure

```
ecourts_scraper/
├── scraper.py              # Main CLI script
├── api_app.py             # Optional Flask API wrapper
├── test_scraper.py        # Test script
├── requirements.txt       # Python dependencies
├── example_output.json    # Sample output format
├── README.md             # This file
├── LICENSE               # MIT license
└── outputs/              # Output directory
    ├── cases/           # Downloaded case PDFs
    ├── causelists/      # Downloaded cause list PDFs
    └── *.json          # Search results
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone or download the project
# Navigate to project directory

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage

```bash
# Check case by CNR for today
python scraper.py --cnr "MHMU01234567890123" --today

# Check case by type/number/year for tomorrow
python scraper.py --type "CR" --number 123 --year 2024 --tomorrow

# Check case for specific date
python scraper.py --cnr "DLCT01234567890123" --date "2024-10-20"

# Download cause list for today
python scraper.py --causelist --today --download-pdf

# Get help
python scraper.py --help
```

### 3. Run Tests

```bash
# Run the test suite
python test_scraper.py
```

### 4. Start API Server (Optional)

```bash
# Start Flask API server
python api_app.py

# Test API endpoints
curl -X POST http://localhost:5001/check \
  -H "Content-Type: application/json" \
  -d '{"cnr":"MHMU01234567890123","date":"2024-10-20"}'
```

## 📖 Detailed Usage

### Command Line Options

#### Case Identification
- `--cnr <CNR>` - Full CNR string (e.g., MHMU01234567890123)
- `--type <TYPE>` - Case type (CR, CIV, FA, CC, etc.)
- `--number <NUM>` - Case number
- `--year <YEAR>` - Case year

#### Date Selection
- `--today` - Check for today's date
- `--tomorrow` - Check for tomorrow's date  
- `--date <YYYY-MM-DD>` - Check for specific date

#### Actions
- `--causelist` - Download entire cause list
- `--download-pdf` - Download any found PDFs

### Examples

```bash
# Search by CNR for today
python scraper.py --cnr "MHMU01234567890123" --today

# Search by case details for tomorrow
python scraper.py --type "CR" --number 456 --year 2024 --tomorrow

# Download cause list with PDFs
python scraper.py --causelist --today --download-pdf

# Search for specific date
python scraper.py --cnr "DLCT01234567890123" --date "2024-10-25"
```

### API Usage

Start the API server:
```bash
python api_app.py
```

API Endpoints:

**POST /check** - Check specific case
```json
{
  "cnr": "MHMU01234567890123",
  "date": "2024-10-20"
}
```

**POST /causelist** - Get cause list
```json
{
  "date": "2024-10-20"
}
```

## 📄 Output Format

Results are saved as JSON files in the `outputs/` directory:

```json
{
  "query": {
    "case_identifier": "MHMU01234567890123",
    "date_checked": "2024-10-20",
    "timestamp": "2024-10-14T10:30:00"
  },
  "listed": true,
  "serial_number": "5",
  "court_name": "District Court, Mumbai",
  "matched_line": "5. CR 123/2024 - State vs. John Doe",
  "case_pdf_link": "https://...",
  "case_pdf_saved": "outputs/cases/case_123.pdf"
}
```

## ⚠️ Important Notes

### Website Limitations
- eCourts website structure may change frequently
- Some courts may not have online cause lists
- Anti-bot protections may limit scraping
- PDF availability varies by court

### Best Practices
- Use reasonable delays between requests
- Respect website terms of service
- Verify results manually for important cases
- Keep the scraper updated if website changes

### Troubleshooting

**Case not found:**
- Verify CNR format (16 characters)
- Check if court publishes online cause lists
- Try different date formats
- Case might not be listed on that date

**Download failures:**
- PDF might not be publicly available
- Network connectivity issues
- Website blocking automated requests

**Website changes:**
- Update URL patterns in `scraper.py`
- Modify parsing selectors as needed
- Consider using Selenium for dynamic content

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_scraper.py
```

Tests include:
- CLI functionality
- Input validation
- Output file generation
- API import verification
- Error handling

## 🔧 Development

### Adding New Features

1. **New Court Support:** Update URL patterns in `search_cause_list_for_case()`
2. **Better Parsing:** Enhance BeautifulSoup selectors
3. **PDF Processing:** Add PDF text extraction with pdfminer.six
4. **Database Storage:** Replace JSON with SQLite/PostgreSQL

### Code Structure

- `scraper.py` - Main CLI application
- `api_app.py` - Flask web API wrapper  
- `test_scraper.py` - Test suite
- `outputs/` - Generated files directory

## 📋 Requirements Met

- ✅ Input case details (CNR or Case Type/Number/Year)
- ✅ Check if listed today or tomorrow
- ✅ Show serial number and court name
- ✅ Download case PDFs (when available)
- ✅ Download entire cause list
- ✅ Console output with status
- ✅ Save results as JSON files
- ✅ CLI options (--today, --tomorrow, --causelist)
- ✅ Optional web API interface
- ✅ Proper error handling
- ✅ Code quality and documentation
- ✅ GitHub submission ready

## 📝 License

MIT License - see LICENSE file for details.

"# ecourts_scraper" 
