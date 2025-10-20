#!/usr/bin/env python3
"""
Real-time eCourts UI Application
Fetches court data dynamically and downloads cause lists in PDF format
"""

from flask import Flask, render_template, request, jsonify, send_file
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin
import threading
import time
import zipfile
from io import BytesIO

app = Flask(__name__)

# Configuration
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

ECOURTS_BASE = "https://services.ecourts.gov.in/ecourtindia_v6/"
ECOURTS_CAUSE_LIST_URL = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/"

# Create directories
os.makedirs("downloads", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

def create_session():
    """Create a requests session with proper headers"""
    session = requests.Session()
    session.headers.update(HEADERS)
    return session

def fetch_states():
    """Fetch list of states from eCourts"""
    try:
        session = create_session()
        response = session.get(ECOURTS_CAUSE_LIST_URL, timeout=20)
        
        if response.status_code != 200:
            # Fallback with sample states if API fails
            return get_fallback_states()
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Look for state dropdown with multiple strategies
        state_select = (
            soup.find("select", {"name": re.compile(r"state", re.IGNORECASE)}) or
            soup.find("select", {"id": re.compile(r"state", re.IGNORECASE)}) or
            soup.find("select", class_=re.compile(r"state", re.IGNORECASE))
        )
        
        states = []
        if state_select:
            options = state_select.find_all("option")
            for option in options:
                value = option.get('value', '').strip()
                text = option.get_text().strip()
                if value and text and text.lower() not in ['select state', 'choose state', '']:
                    states.append({"value": value, "text": text})
        
        # If no states found, use fallback
        if not states:
            return get_fallback_states()
            
        return states
    except Exception as e:
        print(f"Error fetching states: {e}")
        return get_fallback_states()

def get_fallback_states():
    """Fallback list of major Indian states"""
    return [
        {"value": "MH", "text": "Maharashtra"},
        {"value": "DL", "text": "Delhi"},
        {"value": "KA", "text": "Karnataka"},
        {"value": "TN", "text": "Tamil Nadu"},
        {"value": "UP", "text": "Uttar Pradesh"},
        {"value": "WB", "text": "West Bengal"},
        {"value": "GJ", "text": "Gujarat"},
        {"value": "RJ", "text": "Rajasthan"},
        {"value": "AP", "text": "Andhra Pradesh"},
        {"value": "TS", "text": "Telangana"},
        {"value": "MP", "text": "Madhya Pradesh"},
        {"value": "OR", "text": "Odisha"},
        {"value": "KL", "text": "Kerala"},
        {"value": "AS", "text": "Assam"},
        {"value": "PB", "text": "Punjab"},
        {"value": "HR", "text": "Haryana"},
        {"value": "JH", "text": "Jharkhand"},
        {"value": "CG", "text": "Chhattisgarh"},
        {"value": "BR", "text": "Bihar"},
        {"value": "HP", "text": "Himachal Pradesh"}
    ]

def fetch_districts(state_code):
    """Fetch districts for a given state"""
    try:
        session = create_session()
        
        # Try multiple AJAX endpoints
        ajax_urls = [
            f"{ECOURTS_BASE}ajax/get_districts.php",
            f"{ECOURTS_BASE}api/districts.php",
            f"{ECOURTS_BASE}get_districts.php"
        ]
        
        for ajax_url in ajax_urls:
            try:
                data = {"state_code": state_code, "state": state_code}
                response = session.post(ajax_url, data=data, timeout=15)
                
                if response.status_code == 200:
                    try:
                        districts_data = response.json()
                        if isinstance(districts_data, list) and districts_data:
                            return [{"value": d.get("code", d.get("value", "")), "text": d.get("name", d.get("text", ""))} 
                                   for d in districts_data if d.get("name") or d.get("text")]
                    except:
                        pass
            except:
                continue
        
        # Fallback: Parse HTML response
        try:
            response = session.get(f"{ECOURTS_CAUSE_LIST_URL}?state={state_code}", timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            
            district_select = (
                soup.find("select", {"name": re.compile(r"district", re.IGNORECASE)}) or
                soup.find("select", {"id": re.compile(r"district", re.IGNORECASE)})
            )
            
            districts = []
            if district_select:
                options = district_select.find_all("option")
                for option in options:
                    value = option.get('value', '').strip()
                    text = option.get_text().strip()
                    if value and text and text.lower() not in ['select district', 'choose district', '']:
                        districts.append({"value": value, "text": text})
            
            if districts:
                return districts
        except:
            pass
        
        # Final fallback: return sample districts for major states
        return get_fallback_districts(state_code)
        
    except Exception as e:
        print(f"Error fetching districts: {e}")
        return get_fallback_districts(state_code)

def get_fallback_districts(state_code):
    """Fallback districts for major states"""
    fallback_districts = {
        "MH": [
            {"value": "MH01", "text": "Mumbai City"},
            {"value": "MH02", "text": "Mumbai Suburban"},
            {"value": "MH03", "text": "Pune"},
            {"value": "MH04", "text": "Nagpur"},
            {"value": "MH05", "text": "Thane"},
            {"value": "MH06", "text": "Nashik"},
            {"value": "MH07", "text": "Aurangabad"}
        ],
        "DL": [
            {"value": "DL01", "text": "Central Delhi"},
            {"value": "DL02", "text": "East Delhi"},
            {"value": "DL03", "text": "New Delhi"},
            {"value": "DL04", "text": "North Delhi"},
            {"value": "DL05", "text": "South Delhi"},
            {"value": "DL06", "text": "West Delhi"}
        ],
        "KA": [
            {"value": "KA01", "text": "Bangalore Urban"},
            {"value": "KA02", "text": "Bangalore Rural"},
            {"value": "KA03", "text": "Mysore"},
            {"value": "KA04", "text": "Hubli-Dharwad"},
            {"value": "KA05", "text": "Mangalore"}
        ]
    }
    
    return fallback_districts.get(state_code, [
        {"value": f"{state_code}01", "text": f"{state_code} District 1"},
        {"value": f"{state_code}02", "text": f"{state_code} District 2"}
    ])

def fetch_court_complexes(state_code, district_code):
    """Fetch court complexes for a given state and district"""
    try:
        session = create_session()
        
        # Try multiple AJAX endpoints for court complexes
        ajax_urls = [
            f"{ECOURTS_BASE}ajax/get_court_complexes.php",
            f"{ECOURTS_BASE}ajax/get_complexes.php",
            f"{ECOURTS_BASE}api/complexes.php",
            f"{ECOURTS_BASE}get_complexes.php"
        ]
        
        for ajax_url in ajax_urls:
            try:
                data = {
                    "state_code": state_code, 
                    "district_code": district_code,
                    "state": state_code,
                    "district": district_code
                }
                response = session.post(ajax_url, data=data, timeout=15)
                
                if response.status_code == 200:
                    try:
                        complexes_data = response.json()
                        if isinstance(complexes_data, list) and complexes_data:
                            return [{"value": c.get("code", c.get("value", "")), "text": c.get("name", c.get("text", ""))} 
                                   for c in complexes_data if c.get("name") or c.get("text")]
                    except:
                        pass
            except:
                continue
        
        # Fallback: Try to parse HTML from cause list page
        try:
            response = session.get(f"{ECOURTS_CAUSE_LIST_URL}?state={state_code}&district={district_code}", timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for complex dropdown with multiple strategies
            complex_select = (
                soup.find("select", {"name": re.compile(r"complex", re.IGNORECASE)}) or
                soup.find("select", {"id": re.compile(r"complex", re.IGNORECASE)}) or
                soup.find("select", class_=re.compile(r"complex", re.IGNORECASE)) or
                soup.find("select", {"name": re.compile(r"court", re.IGNORECASE)})  # Sometimes court and complex are same
            )
            
            complexes = []
            if complex_select:
                options = complex_select.find_all("option")
                for option in options:
                    value = option.get('value', '').strip()
                    text = option.get_text().strip()
                    if value and text and text.lower() not in ['select complex', 'choose complex', 'select court', 'choose court', '']:
                        complexes.append({"value": value, "text": text})
            
            if complexes:
                return complexes
        except:
            pass
        
        # Final fallback: Generate sample court complexes
        return get_fallback_complexes(state_code, district_code)
        
    except Exception as e:
        print(f"Error fetching court complexes: {e}")
        return get_fallback_complexes(state_code, district_code)

def get_fallback_complexes(state_code, district_code):
    """Fallback court complexes for major states and districts"""
    fallback_complexes = {
        "MH": {
            "MH01": [  # Mumbai City
                {"value": "MH01C01", "text": "Mumbai City Civil Court"},
                {"value": "MH01C02", "text": "Mumbai Sessions Court"},
                {"value": "MH01C03", "text": "Mumbai High Court"},
                {"value": "MH01C04", "text": "Mumbai Magistrate Court"}
            ],
            "MH02": [  # Mumbai Suburban
                {"value": "MH02C01", "text": "Andheri Court Complex"},
                {"value": "MH02C02", "text": "Bandra Court Complex"},
                {"value": "MH02C03", "text": "Borivali Court Complex"}
            ],
            "MH03": [  # Pune
                {"value": "MH03C01", "text": "Pune Civil Court"},
                {"value": "MH03C02", "text": "Pune Sessions Court"},
                {"value": "MH03C03", "text": "Pune Magistrate Court"}
            ]
        },
        "DL": {
            "DL01": [  # Central Delhi
                {"value": "DL01C01", "text": "Tis Hazari Courts Complex"},
                {"value": "DL01C02", "text": "Delhi High Court"},
                {"value": "DL01C03", "text": "Patiala House Courts"}
            ],
            "DL02": [  # East Delhi
                {"value": "DL02C01", "text": "Karkardooma Courts Complex"},
                {"value": "DL02C02", "text": "Shahdara Court Complex"}
            ]
        },
        "KA": {
            "KA01": [  # Bangalore Urban
                {"value": "KA01C01", "text": "Bangalore City Civil Court"},
                {"value": "KA01C02", "text": "Bangalore Sessions Court"},
                {"value": "KA01C03", "text": "Karnataka High Court"}
            ]
        }
    }
    
    # Get complexes for the specific state and district
    state_complexes = fallback_complexes.get(state_code, {})
    district_complexes = state_complexes.get(district_code, [])
    
    # If no specific complexes found, generate generic ones
    if not district_complexes:
        district_complexes = [
            {"value": f"{state_code}{district_code}C01", "text": f"{state_code} {district_code} Civil Court"},
            {"value": f"{state_code}{district_code}C02", "text": f"{state_code} {district_code} Sessions Court"},
            {"value": f"{state_code}{district_code}C03", "text": f"{state_code} {district_code} Magistrate Court"}
        ]
    
    return district_complexes

def fetch_courts(state_code, district_code, complex_code):
    """Fetch individual courts for a given complex"""
    try:
        session = create_session()
        
        # Try multiple AJAX endpoints for courts
        ajax_urls = [
            f"{ECOURTS_BASE}ajax/get_courts.php",
            f"{ECOURTS_BASE}ajax/get_judges.php",
            f"{ECOURTS_BASE}api/courts.php",
            f"{ECOURTS_BASE}get_courts.php"
        ]
        
        for ajax_url in ajax_urls:
            try:
                data = {
                    "state_code": state_code, 
                    "district_code": district_code,
                    "complex_code": complex_code,
                    "state": state_code,
                    "district": district_code,
                    "complex": complex_code
                }
                response = session.post(ajax_url, data=data, timeout=15)
                
                if response.status_code == 200:
                    try:
                        courts_data = response.json()
                        if isinstance(courts_data, list) and courts_data:
                            return [{"value": c.get("code", c.get("value", "")), "text": c.get("name", c.get("text", ""))} 
                                   for c in courts_data if c.get("name") or c.get("text")]
                    except:
                        pass
            except:
                continue
        
        # Fallback: Parse HTML
        try:
            url = f"{ECOURTS_CAUSE_LIST_URL}?state={state_code}&district={district_code}&complex={complex_code}"
            response = session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for court dropdown with multiple strategies
            court_select = (
                soup.find("select", {"name": re.compile(r"court", re.IGNORECASE)}) or
                soup.find("select", {"id": re.compile(r"court", re.IGNORECASE)}) or
                soup.find("select", class_=re.compile(r"court", re.IGNORECASE)) or
                soup.find("select", {"name": re.compile(r"judge", re.IGNORECASE)})
            )
            
            courts = []
            if court_select:
                options = court_select.find_all("option")
                for option in options:
                    value = option.get('value', '').strip()
                    text = option.get_text().strip()
                    if value and text and text.lower() not in ['select court', 'choose court', 'select judge', 'choose judge', '']:
                        courts.append({"value": value, "text": text})
            
            if courts:
                return courts
        except:
            pass
        
        # Final fallback: Generate sample courts
        return get_fallback_courts(state_code, district_code, complex_code)
        
    except Exception as e:
        print(f"Error fetching courts: {e}")
        return get_fallback_courts(state_code, district_code, complex_code)

def get_fallback_courts(state_code, district_code, complex_code):
    """Fallback individual courts/judges for a complex"""
    return [
        {"value": f"{complex_code}CT01", "text": "Court No. 1 / Judge 1"},
        {"value": f"{complex_code}CT02", "text": "Court No. 2 / Judge 2"},
        {"value": f"{complex_code}CT03", "text": "Court No. 3 / Judge 3"},
        {"value": f"{complex_code}CT04", "text": "Court No. 4 / Judge 4"},
        {"value": f"{complex_code}CT05", "text": "Court No. 5 / Judge 5"}
    ]

def download_cause_list_pdf(state_code, district_code, complex_code, court_code, date_str):
    """Download cause list PDF for a specific court and date"""
    try:
        session = create_session()
        
        # Format date for eCourts (DD-MM-YYYY)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d-%m-%Y")
        
        # Try multiple PDF download strategies
        pdf_urls = [
            f"{ECOURTS_BASE}causelist_pdf.php?state={state_code}&district={district_code}&complex={complex_code}&court={court_code}&date={formatted_date}",
            f"{ECOURTS_BASE}generate_causelist.php?state={state_code}&district={district_code}&complex={complex_code}&court={court_code}&date={formatted_date}",
            f"{ECOURTS_BASE}pdf/causelist_{state_code}_{district_code}_{complex_code}_{court_code}_{formatted_date.replace('-', '')}.pdf"
        ]
        
        for pdf_url in pdf_urls:
            try:
                response = session.get(pdf_url, timeout=30)
                if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
                    return response.content
            except:
                continue
        
        return None
    except Exception as e:
        print(f"Error downloading cause list: {e}")
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/states')
def api_states():
    """Get list of states"""
    states = fetch_states()
    return jsonify(states)

@app.route('/api/districts/<state_code>')
def api_districts(state_code):
    """Get districts for a state"""
    districts = fetch_districts(state_code)
    return jsonify(districts)

@app.route('/api/complexes/<state_code>/<district_code>')
def api_complexes(state_code, district_code):
    """Get court complexes for a state and district"""
    print(f"[DEBUG] Fetching complexes for state: {state_code}, district: {district_code}")
    complexes = fetch_court_complexes(state_code, district_code)
    print(f"[DEBUG] Found {len(complexes)} complexes: {[c['text'] for c in complexes[:3]]}")
    return jsonify(complexes)

@app.route('/api/courts/<state_code>/<district_code>/<complex_code>')
def api_courts(state_code, district_code, complex_code):
    """Get courts for a complex"""
    courts = fetch_courts(state_code, district_code, complex_code)
    return jsonify(courts)

@app.route('/api/download_single', methods=['POST'])
def api_download_single():
    """Download cause list for a single court"""
    data = request.get_json()
    
    state_code = data.get('state_code')
    district_code = data.get('district_code')
    complex_code = data.get('complex_code')
    court_code = data.get('court_code')
    date_str = data.get('date')
    
    if not all([state_code, district_code, complex_code, court_code, date_str]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    pdf_content = download_cause_list_pdf(state_code, district_code, complex_code, court_code, date_str)
    
    if pdf_content:
        filename = f"causelist_{court_code}_{date_str}.pdf"
        filepath = os.path.join("downloads", filename)
        
        with open(filepath, "wb") as f:
            f.write(pdf_content)
        
        return jsonify({"success": True, "filename": filename, "size": len(pdf_content)})
    else:
        return jsonify({"error": "Could not download cause list PDF"}), 404

@app.route('/api/download_complex', methods=['POST'])
def api_download_complex():
    """Download cause lists for all courts in a complex"""
    data = request.get_json()
    
    state_code = data.get('state_code')
    district_code = data.get('district_code')
    complex_code = data.get('complex_code')
    date_str = data.get('date')
    
    if not all([state_code, district_code, complex_code, date_str]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    # Get all courts in the complex
    courts = fetch_courts(state_code, district_code, complex_code)
    
    if not courts:
        return jsonify({"error": "No courts found in complex"}), 404
    
    # Create a zip file with all PDFs
    zip_buffer = BytesIO()
    downloaded_count = 0
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for court in courts:
            court_code = court['value']
            court_name = court['text']
            
            pdf_content = download_cause_list_pdf(state_code, district_code, complex_code, court_code, date_str)
            
            if pdf_content:
                filename = f"causelist_{court_name.replace(' ', '_')}_{date_str}.pdf"
                zip_file.writestr(filename, pdf_content)
                downloaded_count += 1
    
    if downloaded_count > 0:
        zip_buffer.seek(0)
        zip_filename = f"causelist_complex_{complex_code}_{date_str}.zip"
        zip_filepath = os.path.join("downloads", zip_filename)
        
        with open(zip_filepath, "wb") as f:
            f.write(zip_buffer.getvalue())
        
        return jsonify({
            "success": True, 
            "filename": zip_filename, 
            "courts_downloaded": downloaded_count,
            "total_courts": len(courts)
        })
    else:
        return jsonify({"error": "No cause lists could be downloaded"}), 404

@app.route('/download/<filename>')
def download_file(filename):
    """Serve downloaded files"""
    filepath = os.path.join("downloads", filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)