import base64, gzip, tarfile, io, pathlib
# app
b64 = "".join(pathlib.Path(f"b64_{i}.txt").read_text().strip() for i in range(4))
pathlib.Path("app.py").write_bytes(gzip.decompress(base64.b64decode(b64)))
print("app.py restored", pathlib.Path("app.py").stat().st_size)
# templates
tpl = "".join(pathlib.Path(f"tpl_{i}.txt").read_text().strip() for i in range(4))
with tarfile.open(fileobj=io.BytesIO(base64.b64decode(tpl)), mode="r:gz") as tar:
    tar.extractall(".")
print("templates", sorted(p.name for p in pathlib.Path("templates").glob("*.html")))
