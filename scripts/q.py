import os
import sqlite3
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
args = sys.argv[1:]

db = ROOT / "analytics.duckdb"
if args and args[0] == "-d":
    db, args = ROOT / args[1], args[2:]

from_file = bool(args) and args[0] == "-f"
sql = Path(args[1]).read_text(encoding="utf-8") if from_file else " ".join(args)

os.chdir(ROOT / "dbt_project")  # supaya '../data/...' di SQL selalu benar

if db.suffix == ".sqlite":
    con = sqlite3.connect(db)
    cur = None
    if from_file:
        con.executescript(sql)
    else:
        cur = con.execute(sql)
    con.commit()
else:
    con = duckdb.connect(str(db))
    cur = con.execute(sql)

if cur is not None and cur.description:
    print([d[0] for d in cur.description])
    for row in cur.fetchall():
        print(row)
con.close()