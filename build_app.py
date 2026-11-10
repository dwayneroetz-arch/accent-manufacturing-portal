import base64, tarfile, io, pathlib
parts = []
FIXES = [(0, 370, '3'), (0, 737, 'l'), (0, 1529, '9'), (0, 2342, '5'), (0, 3432, '1'), (2, 1898, 'U'), (2, 1899, 's'), (3, 3374, '6'), (5, 2809, 'R'), (6, 609, 'S'), (6, 3081, 'l')]
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
print("templates", sorted(p.name for p in pathlib.Path("templates").glob("*.html")))
