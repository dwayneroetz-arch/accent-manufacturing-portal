import base64, tarfile, io, pathlib, re

# Clean package – no character FIXES required
parts = []
for i in range(8):
    p = pathlib.Path(f"pkg_{i}.txt")
    if not p.exists():
        raise SystemExit(f"missing {p}")
    parts.append(p.read_text().strip())
data = "".join(parts)

with tarfile.open(fileobj=io.BytesIO(base64.b64decode(data)), mode="r:gz") as tar:
    tar.extractall(".")
print("restored", pathlib.Path("app.py").stat().st_size, "bytes")

pathlib.Path("static").mkdir(exist_ok=True)

# Overlay theme from hex parts if present (allows theme-only updates without repackaging)
hexes = [pathlib.Path(f"static/th{i}.hex") for i in range(4)]
if all(h.exists() for h in hexes):
    theme_css = bytes.fromhex("".join(h.read_text().strip() for h in hexes)).decode("utf-8")
    pathlib.Path("static/theme.css").write_text(theme_css)
    print("theme.css from hex", len(theme_css))
    # Keep base.html in sync with the same CSS (inline = reliable)
    base = pathlib.Path("templates/base.html")
    if base.exists():
        html = base.read_text()
        new_style = "<style>\n" + theme_css + "\n{% block extra_css %}{% endblock %}\n</style>"
        if re.search(r"<style>.*?</style>", html, flags=re.S):
            html = re.sub(r"<style>.*?</style>", new_style, html, count=1, flags=re.S)
            base.write_text(html)
            print("base.html style synced from hex")
elif pathlib.Path("static/theme.css").exists():
    print("theme.css present in package")

# Ensure static route exists
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

print("build complete – industrial safety theme + mobile layout ready")
