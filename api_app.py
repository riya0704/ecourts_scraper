#!/usr/bin/env python3
"""
api_app.py - simple Flask wrapper to expose the scraper functionality via HTTP API.
This is optional and meant to be run locally for quick checks.

Run:
    pip install -r requirements.txt
    python api_app.py

Endpoints:
- POST /check  with JSON { "cnr": "...", "date": "YYYY-MM-DD" }
- POST /causelist with JSON { "date": "YYYY-MM-DD" }
"""
from flask import Flask, request, jsonify
from datetime import datetime
import importlib.util, os

spec = importlib.util.spec_from_file_location("scraper_module", os.path.join(os.path.dirname(__file__), "scraper.py"))
scraper_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_module)

app = Flask(__name__)

@app.route("/check", methods=["POST"])
def check():
    data = request.get_json() or {}
    cnr = data.get("cnr")
    date_str = data.get("date") or datetime.now().strftime("%Y-%m-%d")
    if not cnr:
        return jsonify({"error":"provide 'cnr' in JSON body"}), 400
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return jsonify({"error":"date must be YYYY-MM-DD"}), 400
    res = scraper_module.search_cause_list_for_case(cnr, d)
    return jsonify(res)

@app.route("/causelist", methods=["POST"])
def causelist():
    data = request.get_json() or {}
    date_str = data.get("date") or datetime.now().strftime("%Y-%m-%d")
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return jsonify({"error":"date must be YYYY-MM-DD"}), 400
    res = scraper_module.search_cause_list_for_case("", d)
    return jsonify(res)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
