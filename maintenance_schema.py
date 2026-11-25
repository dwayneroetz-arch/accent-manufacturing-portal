# --- Maintenance Hub schema + helpers (injected) ---
def _ensure_maint_hub_schema():
    conn = get_db()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        contact_name TEXT,
        email TEXT,
        phone TEXT,
        speciality TEXT,
        notes TEXT,
        created_at TEXT);
    CREATE TABLE IF NOT EXISTS tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_no TEXT UNIQUE NOT NULL,
        created_at TEXT,
        type TEXT,
        asset_code TEXT,
        title TEXT,
        status TEXT DEFAULT 'Open',
        notes TEXT);
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_no TEXT,
        asset_code TEXT,
        title TEXT NOT NULL,
        description TEXT,
        priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Open',
        due_date TEXT,
        created_at TEXT,
        completed_at TEXT,
        notes TEXT);
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_no TEXT,
        supplier_id INTEGER,
        asset_code TEXT,
        description TEXT,
        message TEXT,
        status TEXT DEFAULT 'Requested',
        amount REAL,
        follow_up_date TEXT,
        created_at TEXT,
        notes TEXT);
    CREATE TABLE IF NOT EXISTS fuel_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_no TEXT,
        litres REAL,
        status TEXT DEFAULT 'Submitted',
        created_at TEXT,
        notes TEXT,
        email_sent INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_no TEXT,
        event_type TEXT,
        message TEXT,
        created_at TEXT,
        user_name TEXT DEFAULT 'Maintenance');
    """)
    conn.commit()
    conn.close()

def next_tracking_no(conn):
    year = datetime.now().year
    prefix = f"MT-{year}-"
    row = conn.execute(
        "SELECT tracking_no FROM tracking WHERE tracking_no LIKE ? ORDER BY id DESC LIMIT 1",
        (prefix + "%",)
    ).fetchone()
    if row:
        try:
            num = int(row["tracking_no"].split("-")[-1]) + 1
        except Exception:
            num = 1
    else:
        num = 1
    return f"{prefix}{num:04d}"

def log_activity(conn, tracking_no, event_type, message):
    conn.execute(
        "INSERT INTO activity_log (tracking_no, event_type, message, created_at) VALUES (?,?,?,?)",
        (tracking_no, event_type, message, datetime.now().isoformat(timespec="seconds"))
    )
