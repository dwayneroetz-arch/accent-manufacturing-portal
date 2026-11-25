import base64, tarfile, io, pathlib, re, sys

pathlib.Path("static").mkdir(exist_ok=True)

def extract_clean():
    parts = []
    for i in range(8):
        p = pathlib.Path(f"pkg_{i}.txt")
        if not p.exists():
            return False
        parts.append(p.read_text().strip())
    data = "".join(parts)
    try:
        with tarfile.open(fileobj=io.BytesIO(base64.b64decode(data)), mode="r:gz") as tar:
            tar.extractall(".")
        print("restored clean package", pathlib.Path("app.py").stat().st_size, "bytes")
        return True
    except Exception as e:
        print("clean extract failed:", e)
        return False

def extract_with_fixes():
    FIXES = [(0, 370, "3"), (0, 737, "l"), (0, 1529, "9"), (0, 2342, "5"), (0, 3432, "1"),
             (2, 1898, "U"), (2, 1899, "s"), (3, 3374, "6"), (5, 2809, "R"), (6, 609, "S"), (6, 3081, "l")]
    parts = []
    for i in range(8):
        p = pathlib.Path(f"pkg_{i}.txt")
        if not p.exists():
            raise SystemExit(f"missing {p}")
        t = list(p.read_text().strip())
        for pi, pos, ch in FIXES:
            if pi == i and pos < len(t):
                t[pos] = ch
        parts.append("".join(t))
    data = "".join(parts)
    with tarfile.open(fileobj=io.BytesIO(base64.b64decode(data)), mode="r:gz") as tar:
        tar.extractall(".")
    print("restored package with FIXES", pathlib.Path("app.py").stat().st_size, "bytes")

if not extract_clean():
    extract_with_fixes()

hexes = [pathlib.Path(f"static/th{i}.hex") for i in range(4)]
if all(h.exists() for h in hexes):
    theme_css = bytes.fromhex("".join(h.read_text().strip() for h in hexes)).decode("utf-8")
    if "move-form" not in theme_css:
        theme_css += "\n.line-rect-sm{min-height:36px;font-size:.8rem;padding:.3rem .4rem;margin-bottom:0!important}\n"
    pathlib.Path("static/theme.css").write_text(theme_css)
    print("theme.css from hex", len(theme_css))
    base = pathlib.Path("templates/base.html")
    if base.exists():
        html = base.read_text()
        new_style = "<style>\n" + theme_css + "\n{% block extra_css %}{% endblock %}\n</style>"
        if re.search(r"<style>.*?</style>", html, flags=re.S):
            html = re.sub(r"<style>.*?</style>", new_style, html, count=1, flags=re.S)
            base.write_text(html)

pa_parts = [pathlib.Path(f"pa_{i}.txt") for i in range(12)]
if all(p.exists() for p in pa_parts) and all(p.stat().st_size > 20 for p in pa_parts):
    pathlib.Path("templates").mkdir(exist_ok=True)
    pathlib.Path("templates/production.html").write_bytes(
        base64.b64decode("".join(p.read_text().strip() for p in pa_parts))
    )
    print("production.html written")

app_path = pathlib.Path("app.py")
app = app_path.read_text()
if "send_from_directory" not in app:
    app = app.replace(
        "from flask import Flask, render_template, request, redirect, url_for, flash",
        "from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory",
    )
    needle = "\ninit_db()\n"
    route = ('\n@app.route("/static/<path:filename>")\n'
             "def static_files(filename):\n"
             '    return send_from_directory("static", filename)\n\n'
             "init_db()\n")
    if needle in app:
        app = app.replace(needle, route, 1)
        app_path.write_text(app)

print("build complete")

side_dir = pathlib.Path("_committed_templates")
if side_dir.exists():
    pathlib.Path("templates").mkdir(exist_ok=True)
    for side in side_dir.glob("*.html"):
        dest = pathlib.Path("templates") / side.name
        dest.write_text(side.read_text())
        print("Restored committed template", side.name)

print("Using restored package app.py")

extra = pathlib.Path("maintenance_extra.py")
app_path = pathlib.Path("app.py")
if extra.exists() and app_path.exists():
    app_txt = app_path.read_text()
    if "def maintenance_hub" not in app_txt:
        marker = "# ---------- PRODUCTION ----------"
        if marker in app_txt:
            app_txt = app_txt.replace(marker, extra.read_text() + "\n\n" + marker)
            app_path.write_text(app_txt)
            print("Injected Maintenance Hub routes into app.py")
    else:
        print("Maintenance Hub routes already present")

schema_f = pathlib.Path("maintenance_schema.py")
if schema_f.exists() and app_path.exists():
    app_txt = app_path.read_text()
    if "def next_tracking_no" not in app_txt:
        needle = "def get_db():\n    conn = sqlite3.connect(DATABASE)\n    conn.row_factory = sqlite3.Row\n    return conn\n"
        if needle in app_txt:
            app_txt = app_txt.replace(needle, needle + "\n" + schema_f.read_text() + "\n")
            app_path.write_text(app_txt)
            print("Injected schema + helpers")
    else:
        print("Schema/helpers already present")

app_txt = app_path.read_text()
if "def _ensure_maint_hub_schema" in app_txt and "init_db()\n_ensure_maint_hub_schema()" not in app_txt:
    if "\ninit_db()\n\nif __name__" in app_txt:
        app_txt = app_txt.replace("\ninit_db()\n\nif __name__", "\ninit_db()\n_ensure_maint_hub_schema()\n\nif __name__", 1)
        app_path.write_text(app_txt)
        print("Added _ensure_maint_hub_schema() call after init_db()")
    elif "\ninit_db()\n" in app_txt:
        parts = app_txt.rsplit("\ninit_db()\n", 1)
        if len(parts) == 2:
            app_txt = parts[0] + "\ninit_db()\n_ensure_maint_hub_schema()\n" + parts[1]
            app_path.write_text(app_txt)
            print("Added _ensure_maint_hub_schema() call (rsplit)")

plant = pathlib.Path("plant_patch.py")
if plant.exists() and app_path.exists():
    app_txt = app_path.read_text()
    if "open_breakdowns" not in app_txt:
        marker = "@app.route(\"/\")\ndef landing():"
        if marker in app_txt:
            start = app_txt.find(marker)
            end_markers = ["# ---------- ADMIN", "@app.route(\"/admin\")", "# ---------- MAINTENANCE"]
            end = -1
            for em in end_markers:
                i = app_txt.find(em, start + 10)
                if i != -1:
                    end = i
                    break
            if start != -1 and end != -1:
                app_txt = app_txt[:start] + plant.read_text() + "\n\n" + app_txt[end:]
                app_path.write_text(app_txt)
                print("Patched landing + line_detail with breakdown reasons")
            else:
                print("Could not locate landing/line_detail block to patch")
        else:
            print("landing route marker not found")
    else:
        print("Plant breakdown reasons already present")

for name in ("landing.html", "line_detail.html"):
    side = pathlib.Path("_committed_templates") / name
    dest = pathlib.Path("templates") / name
    if side.exists():
        dest.write_text(side.read_text())
        print("Restored committed template", name)
