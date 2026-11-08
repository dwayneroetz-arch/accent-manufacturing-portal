from pathlib import Path
a = Path("build_app_a.txt").read_text()
b = Path("build_app_b.txt").read_text()
exec(a+b)
