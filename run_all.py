"""Poora pipeline ek command mein: python run_all.py"""
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).parent / "src"
steps = ["generate_data.py", "01_cleaning.py", "run_sql.py", "02_eda.py", "03_rfm.py"]

for s in steps:
    print(f"\n{'=' * 60}\n>> {s}\n{'=' * 60}")
    r = subprocess.run([sys.executable, s], cwd=SRC)
    if r.returncode != 0:
        sys.exit(f"Step failed: {s}")

print("\nDone! Results: outputs/ folder, charts: outputs/charts/")
