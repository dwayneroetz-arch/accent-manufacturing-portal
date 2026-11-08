# Accent Manufacturing Portal  
**Production + Maintenance** (adhesive putty plant)

Integrated web portal for Accent Manufacturing:

- **Production** – orders, recipes, stock, mixing stations, packing hall  
- **Maintenance** – assets by department, running/tea/lunch schedules, downtime, planned maintenance & redundancy, upgrades with cloud-drive quote links, overview dashboard  

Built as a single Flask + SQLite app (same architecture as the original production workflow).

## Screens

| Area | Path | Purpose |
|------|------|---------|
| Production Admin | `/` | Orders, stock, assign mixers |
| Packing Hall | `/packing` | Large packing status board |
| Mixing Station 1–3 | `/mixing/1` … `/3` | Recipe + weigh-out screens |
| **Maintenance Dashboard** | `/maintenance` | Overview of all assets & departments |
| **Assets** | `/maintenance/assets` | Create & list assets |
| **Asset detail** | `/maintenance/asset/<id>` | Schedule, downtime, PM, upgrades |
| **Departments** | `/maintenance/departments` | Mixing Hall, Production, … |

## Maintenance features

- Allocate assets to **Mixing Hall** or **Production** (or add more departments)
- Per-asset **running times**, **tea** and **lunch** breaks (editable by maintenance manager)
- Live **downtime / breakdown** log with reason + allocated resolution time; close with actual resolution
- **Planned maintenance** and **redundancy** records (reason, resolution, schedule)
- **Upgrades** with cost, estimated hours, and a **cloud-drive link** to third-party quotes for management to open
- Dashboard KPIs: total / operational / down / in maintenance + recent events

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:

- http://127.0.0.1:5000/              → Production Admin  
- http://127.0.0.1:5000/maintenance  → Maintenance Dashboard  

SQLite database (`putty.db`) is created automatically with sample production + maintenance data.

## Deploy

Same options as before (Render, Cloudflare Tunnel, Railway, etc.).  
Build: `pip install -r requirements.txt`  
Start: `python app.py`

Change `app.secret_key` before real production use. For multi-user / multi-site, move to PostgreSQL and add authentication.

## License

MIT – free to use and modify for your factory.
