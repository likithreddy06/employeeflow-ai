# EmployeeFlow AI

A small, runnable employee-management AI agent built for the 24-hour challenge. It takes an employee HR request, identifies the request type, extracts useful details, recommends an action, and stores the request in SQLite.

## What it does

**Input:** employee name, department, and a natural-language request.  
**Output:** category, priority, owner, suggested action, extracted dates, and a record saved in the dashboard.

Supported categories: leave, payroll, onboarding, IT access, performance, benefits, and general HR.

## Run locally

**Quickest option (no installation):** double-click `demo.html`. It opens a fully interactive, browser-only demonstration.

```bash
cd employee_management_ai
python -m venv .venv
.venv\\Scripts\\activate       # Windows
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

No API key is required. The included classification logic is deliberately deterministic so the demo is reproducible and does not send employee data to a third party.

## Sample inputs

| Employee | Request | Expected result |
|---|---|---|
| Priya Shah | `I need leave from 14 August to 16 August for a family event.` | Leave → HR Operations → Normal |
| Arjun Mehta | `My salary for July is missing. Please resolve today.` | Payroll → Finance & Payroll → High |
| Neha Rao | `I start Monday and need my laptop, email, and Slack access.` | Onboarding → People Operations → High |

## Design and tradeoffs

- **Approach:** keyword intent detection plus urgency signals and date extraction. This is transparent and easy to test for a short challenge.
- **Storage:** SQLite keeps the project self-contained and enables review of prior requests.
- **AI extension:** In production, replace `analyze_request` with an LLM structured-output call and retain validation rules before saving.
- **Limitations:** keyword classification can miss unusual wording; it is a demo workflow, not an HR system of record.

## Project layout

- `app.py` — Flask app, SQLite access, and request-analysis agent
- `templates/index.html` — dashboard UI
- `static/styles.css` — visual styling
- `sample_requests.json` — reproducible demo data
