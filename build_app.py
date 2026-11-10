import base64, tarfile, io, pathlib
data = "".join(pathlib.Path(f"pkg_{i}.txt").read_text().strip() for i in range(8))
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(data)), mode="r:gz") as tar:
    tar.extractall(".")
print("restored app", pathlib.Path("app.py").stat().st_size)
print("templates", sorted(p.name for p in pathlib.Path("templates").glob("*.html")))
