"""
sql/analysis_queries.sql ki saari queries SQLite DB par chalata hai
aur results outputs/sql_results.txt mein save karta hai.
"""
import re
import sqlite3
import pandas as pd
from config import ROOT, DB_PATH, OUTPUTS

sql_text = (ROOT / "sql" / "analysis_queries.sql").read_text(encoding="utf-8")
blocks = [b.strip() for b in sql_text.split(";") if "SELECT" in b.upper() or "WITH" in b.upper()]

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

out = []
with sqlite3.connect(DB_PATH) as con:
    for b in blocks:
        m = re.search(r"--\s*(Q\d+\..*)", b)
        title = m.group(1) if m else "Query"
        df = pd.read_sql_query(b, con)
        out.append(f"=== {title} ===\n{df.head(15).to_string(index=False)}\n")
        print(out[-1])

(OUTPUTS / "sql_results.txt").write_text("\n".join(out), encoding="utf-8")
