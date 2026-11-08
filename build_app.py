from pathlib import Path
code = "".join(Path(f"part{i}.txt").read_text() for i in range(4))
exec(code)
