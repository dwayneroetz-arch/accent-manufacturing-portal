# Deploy Accent Portal on Render

## Repo
https://github.com/dwayneroetz-arch/accent-manufacturing-portal

## Steps (Dashboard)

1. Log in at https://dashboard.render.com
2. **New +** → **Web Service**
3. Connect GitHub → select **dwayneroetz-arch/accent-manufacturing-portal**
4. Configure:
   - **Name:** accent-manufacturing-portal
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python build_app.py`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
   - **Plan:** Free
5. Add environment variable: `RENDER` = `true`
6. **Create Web Service** and wait for the deploy to finish
7. Open your service URL from the Render dashboard

## After go-live

| Page | Path |
|------|------|
| Admin / Orders | `/` |
| Recipes | `/?tab=recipes` |
| Maintenance | `/maintenance` |
| Packing | `/packing` |
| Mixer 1 | `/mixing/1` |

## Free tier notes

- Sleeps after idle; cold start ~30–60s
- SQLite data resets on redeploy — OK for pilot; we can add Postgres for permanent data
