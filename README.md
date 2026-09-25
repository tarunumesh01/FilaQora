# FilaQora

Custom **customer management system** with CRM, live analytics, CSV/Excel export, and a REST API.

**Repository:** [github.com/tarunumesh01/FilaQora](https://github.com/tarunumesh01/FilaQora)  
**Contact:** tarunumesh23@gmail.com · [LinkedIn](https://www.linkedin.com/in/tarun-u-1020423ba/)

---

## Features

- Customer CRM with search, tags, and company management
- Live dashboard with growth charts, top companies, and tag analytics
- CSV & Excel export
- REST API secured with Bearer tokens
- Public live demo page
- PostgreSQL in production, SQLite for local development

---

## Quick Start (Local)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # optional
python app.py