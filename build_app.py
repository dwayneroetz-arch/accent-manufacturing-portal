import base64, gzip, pathlib
b64 = "".join(pathlib.Path(f"b64_{i}.txt").read_text().strip() for i in range(4))
pathlib.Path("app.py").write_bytes(gzip.decompress(base64.b64decode(b64)))
print("app.py restored", pathlib.Path("app.py").stat().st_size)
