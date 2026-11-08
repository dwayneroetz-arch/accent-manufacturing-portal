# Accent Manufacturing Portal

Production + Maintenance portal for adhesive putty manufacturing.

## Features

- **Orders** – unit-based orders, auto recipe scale, stock deducted on order place
- **Recipes** – products with unit size (g), ingredient g/unit or total-kg batch entry
- **Stock** – live raw material levels
- **Mixing / Packing** – station screens
- **Maintenance** – assets, downtime, planned work, upgrades + quote links

## Deploy on Render

1. Connect this GitHub repo on [render.com](https://render.com)
2. New **Web Service** → select `accent-manufacturing-portal`
3. Settings:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
4. Create Web Service

Or use Blueprint: New → Blueprint → select this repo (`render.yaml`).

## Local run

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000/

## Note on SQLite

Free Render instances use ephemeral disk — the database resets when the service sleeps or redeploys. For permanent production data, add a Render PostgreSQL database later.

## License

MIT
