import base64, tarfile, io, pathlib, re
FIXES = [(0, 370, "3"), (0, 737, "l"), (0, 1529, "9"), (0, 2342, "5"), (0, 3432, "1"),
         (2, 1898, "U"), (2, 1899, "s"), (3, 3374, "6"), (5, 2809, "R"), (6, 609, "S"), (6, 3081, "l")]
parts = []
for i in range(8):
    t = list(pathlib.Path(f"pkg_{i}.txt").read_text().strip())
    for pi, pos, ch in FIXES:
        if pi == i and pos < len(t):
            t[pos] = ch
    parts.append("".join(t))
data = "".join(parts)
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(data)), mode="r:gz") as tar:
    tar.extractall(".")
print("restored", pathlib.Path("app.py").stat().st_size)
pathlib.Path("static").mkdir(exist_ok=True)
# Assemble theme from parts if present
hexes = [pathlib.Path(f"static/th{i}.hex") for i in range(4)]
if all(h.exists() for h in hexes):
    pathlib.Path("static/theme.css").write_bytes(bytes.fromhex("".join(h.read_text().strip() for h in hexes)))

base = pathlib.Path("templates/base.html")
html = base.read_text()
link = '<link rel="stylesheet" href="/static/theme.css">\n'
html = re.sub(r"<style>.*?</style>", link, html, count=1, flags=re.S)
if "navbar-toggler" not in html:
    html = html.replace(
        '<div class="navbar-nav ms-auto flex-row gap-2">',
        '<button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMain" aria-label="Menu"><span class="navbar-toggler-icon"></span></button><div class="collapse navbar-collapse" id="navMain"><div class="navbar-nav ms-auto">'
    )
    html = html.replace('</div>\n  </div>\n</nav>', '</div></div>\n  </div>\n</nav>')
base.write_text(html)
app = pathlib.Path("app.py").read_text()
if "send_from_directory" not in app:
    app = app.replace(
        "from flask import Flask, render_template, request, redirect, url_for, flash",
        "from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory",
    )
    needle = "\ninit_db()\n"
    route = "\n@app.route(\"/static/<path:filename>\")\ndef static_files(filename):\n    return send_from_directory(\"static\", filename)\n\ninit_db()\n"
    if needle in app:
        app = app.replace(needle, route, 1)
    pathlib.Path("app.py").write_text(app)
print("industrial theme linked")
