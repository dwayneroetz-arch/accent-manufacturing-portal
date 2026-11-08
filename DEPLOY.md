# Deploy Accent Portal on Render

## Repo
https://github.com/dwayneroetz-arch/accent-manufacturing-portal

## Option A – Render Dashboard (recommended)

1. Log in at https://dashboard.render.com
2. **New +** → **Web Service**
3. Connect GitHub account if not already connected
4. Select repository: **dwayneroetz-arch/accent-manufacturing-portal**
5. Settings:
   - **Name:** accent-manufacturing-portal
   - **Region:** closest to you (e.g. Frankfurt or Oregon)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python build_app.py`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
   - **Instance type:** Free
6. Click **Create Web Service**
7. Wait 2–5 minutes for the first deploy
8. Open the URL Render gives you (e.g. `https://accent-manufacturing-portal.onrender.com`)

## Option B – Blueprint

1. **New +** → **Blueprint**
2. Select the same repo (uses `render.yaml`)
3. Apply

## After deploy

- Admin: `https://YOUR-SERVICE.onrender.com/`
- Recipes: `https://YOUR-SERVICE.onrender.com/?tab=recipes`
- Maintenance: `https://YOUR-SERVICE.onrender.com/maintenance`

## Important (Free tier)

- Service **sleeps** after ~15 min idle; first request can take 30–60s to wake
- SQLite database is **ephemeral** (resets on redeploy/sleep). Fine for trials; for permanent data we can add Render Postgres later
