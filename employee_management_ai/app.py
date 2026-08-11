from __future__ import annotations

import re
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("employee_requests.db")

RULES = {
    "Leave": {
        "keywords": ["leave", "vacation", "holiday", "sick", "pto", "time off"],
        "owner": "HR Operations",
        "action": "Check leave balance, confirm dates, and route for manager approval.",
    },
    "Payroll": {
        "keywords": ["salary", "payroll", "payslip", "reimbursement", "bonus", "payment", "tax"],
        "owner": "Finance & Payroll",
        "action": "Verify payroll record and reply with the correction timeline.",
    },
    "Onboarding": {
        "keywords": ["start", "onboard", "joining", "new hire", "orientation"],
        "owner": "People Operations",
        "action": "Create an onboarding checklist and coordinate required access.",
    },
    "IT access": {
        "keywords": ["laptop", "email", "slack", "access", "password", "vpn", "software"],
        "owner": "IT Support",
        "action": "Open an IT access ticket and confirm the requested systems.",
    },
    "Performance": {
        "keywords": ["review", "performance", "feedback", "promotion", "goal", "appraisal"],
        "owner": "HR Business Partner",
        "action": "Arrange a confidential discussion and review the relevant performance cycle.",
    },
    "Benefits": {
        "keywords": ["insurance", "benefit", "medical", "health", "claim", "policy"],
        "owner": "Benefits Team",
        "action": "Verify eligibility and share the applicable benefits guidance.",
    },
}


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL, department TEXT, request_text TEXT NOT NULL,
            category TEXT NOT NULL, priority TEXT NOT NULL, owner TEXT NOT NULL,
            action TEXT NOT NULL, dates TEXT, created_at TEXT NOT NULL
        )""")


def analyze_request(text: str) -> dict:
    clean = text.lower()
    matches = {name: sum(word in clean for word in spec["keywords"]) for name, spec in RULES.items()}
    category = max(matches, key=matches.get)
    if matches[category] == 0:
        category = "General HR"
        spec = {"owner": "HR Operations", "action": "Review the request and contact the employee for any missing details."}
    else:
        spec = RULES[category]

    urgent = ["urgent", "asap", "today", "immediately", "cannot", "locked out", "missing"]
    priority = "High" if any(word in clean for word in urgent) else "Normal"
    dates = re.findall(r"\b(?:\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|\d{1,2}\s+(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?))\b", clean, re.I)
    reasons = [f"Matched {category.lower()} request signals"]
    if priority == "High":
        reasons.append("Urgency language detected")
    if dates:
        reasons.append("Date(s) extracted: " + ", ".join(dates))
    return {"category": category, "priority": priority, "owner": spec["owner"], "action": spec["action"], "dates": ", ".join(dates) or "Not stated", "reasoning": "; ".join(reasons)}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/requests")
def list_requests():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM requests ORDER BY id DESC LIMIT 50").fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/analyze")
def create_request():
    data = request.get_json(force=True)
    name, department, text = (data.get("employee_name", "").strip(), data.get("department", "").strip(), data.get("request", "").strip())
    if not name or not text:
        return jsonify({"error": "Employee name and request are required."}), 400
    result = analyze_request(text)
    created_at = datetime.now().strftime("%d %b %Y, %H:%M")
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("INSERT INTO requests (employee_name, department, request_text, category, priority, owner, action, dates, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, department, text, result["category"], result["priority"], result["owner"], result["action"], result["dates"], created_at))
        record_id = cur.lastrowid
    return jsonify({"id": record_id, "employee_name": name, "department": department, "request_text": text, "created_at": created_at, **result})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
