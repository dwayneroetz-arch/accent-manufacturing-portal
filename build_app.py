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

# Theme from hex + production compact CSS
hexes = [pathlib.Path(f"static/th{i}.hex") for i in range(4)]
if all(h.exists() for h in hexes):
    theme_css = bytes.fromhex("".join(h.read_text().strip() for h in hexes)).decode("utf-8")
    if "move-form" not in theme_css:
        theme_css += """
.line-rect-sm{min-height:36px;font-size:.8rem;padding:.3rem .4rem;margin-bottom:0!important}
.line-sub{font-size:.65rem;color:var(--muted);line-height:1.2;margin-top:.15rem;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mixer-block{min-width:4.5rem;text-align:center}
.move-form{display:flex;flex-wrap:wrap;gap:.25rem;align-items:center;max-width:22rem}
.move-form .form-select{width:auto;min-width:5.5rem;max-width:7rem;font-size:.75rem;padding:.2rem .35rem;height:auto}
.move-form .btn{padding:.2rem .5rem;font-size:.75rem;white-space:nowrap}
.move-cell{min-width:11rem}
.table-orders td,.table-orders th{padding:.35rem .45rem;vertical-align:middle}
.stock-scroll{max-height:min(70vh,520px);overflow-y:auto}
@media(max-width:991.98px){.stock-scroll{max-height:220px}.move-form{max-width:100%}}
@media(max-width:575.98px){.line-rect-sm{min-height:34px;font-size:.72rem}.move-form .form-select{min-width:4.8rem;max-width:6rem;font-size:.7rem}.table-orders{font-size:.75rem}.move-cell{min-width:0}}
"""
    pathlib.Path("static/theme.css").write_text(theme_css)
    print("theme.css from hex", len(theme_css))
    base = pathlib.Path("templates/base.html")
    if base.exists():
        html = base.read_text()
        new_style = "<style>\n" + theme_css + "\n{% block extra_css %}{% endblock %}\n</style>"
        if re.search(r"<style>.*?</style>", html, flags=re.S):
            html = re.sub(r"<style>.*?</style>", new_style, html, count=1, flags=re.S)
            base.write_text(html)
            print("base.html style synced from hex")

# Prefer pa_*.txt (12 small parts), fall back to prod_*.txt
pa_parts = [pathlib.Path(f"pa_{i}.txt") for i in range(12)]
prod_parts = [pathlib.Path(f"prod_{i}.txt") for i in range(8)]
if all(p.exists() for p in pa_parts) and all(p.stat().st_size > 20 for p in pa_parts):
    pathlib.Path("templates").mkdir(exist_ok=True)
    pathlib.Path("templates/production.html").write_bytes(
        base64.b64decode("".join(p.read_text().strip() for p in pa_parts))
    )
    print("production.html compact layout written (pa_*)")
elif all(p.exists() for p in prod_parts) and all(p.stat().st_size > 20 for p in prod_parts):
    pathlib.Path("templates").mkdir(exist_ok=True)
    pathlib.Path("templates/production.html").write_bytes(
        base64.b64decode("".join(p.read_text().strip() for p in prod_parts))
    )
    print("production.html compact layout written (prod_*)")
else:
    print("production compact parts incomplete, keeping package template")

app_path = pathlib.Path("app.py")
app = app_path.read_text()
if "send_from_directory" not in app:
    app = app.replace(
        "from flask import Flask, render_template, request, redirect, url_for, flash",
        "from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory",
    )
    needle = "\ninit_db()\n"
    route = (
        '\n@app.route("/static/<path:filename>")\n'
        "def static_files(filename):\n"
        '    return send_from_directory("static", filename)\n\n'
        "init_db()\n"
    )
    if needle in app:
        app = app.replace(needle, route, 1)
        app_path.write_text(app)
        print("added static_files route")

print("build complete – industrial safety theme + production fit")
