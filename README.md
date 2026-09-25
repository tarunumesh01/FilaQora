# FilaQora

Custom **customer management system** — CRM, live analytics, CSV/Excel export, and REST API.

**Repo:** https://github.com/tarunumesh01/FilaQora  
**Contact:** tarunumesh23@gmail.com · [LinkedIn](https://www.linkedin.com/in/tarun-u-1020423ba/)

## Features

- Customer CRM (search, tags, companies)
- Dashboard charts (growth, top companies, tags)
- CSV & Excel export
- REST API with Bearer tokens
- Public live demo page
- PostgreSQL on production (SQLite locally)

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # optional
python app.py
```

Open http://127.0.0.1:5000  

Default admin (first run): `admin@filaqora.com` / `admin123`  
Override with env vars `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_NAME`.

## Environment

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret (required on Render) |
| `DATABASE_URL` | Postgres URL (Render provides this) |
| `ADMIN_EMAIL` | Seed admin email |
| `ADMIN_PASSWORD` | Seed admin password |

## Deploy on Render

1. Push this repo to GitHub.
2. [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint** (uses `render.yaml`)  
   **or** New Web Service + New PostgreSQL manually.
3. Connect repo `tarunumesh01/FilaQora`.
4. Set env:
   - `SECRET_KEY` (generate)
   - `DATABASE_URL` (link Postgres)
   - Optional: `ADMIN_EMAIL`, `ADMIN_PASSWORD`
5. Deploy. Open the service URL and log in with the admin credentials.

**Start command:**  
`gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2`

**Build command:**  
`pip install -r requirements.txt`

## API

All `/api/*` routes require:

```
Authorization: Bearer YOUR_API_TOKEN
```

Token is shown on the **Profile** page after login.

- `GET /api/customers?q=&page=&per_page=`
- `GET /api/customers/<id>`
- `POST /api/customers`
- `PUT /api/customers/<id>`
- `DELETE /api/customers/<id>`

## License

GPL-3.0 (see LICENSE).
