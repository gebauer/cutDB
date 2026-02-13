#!/usr/bin/env python3
"""
Convert a MySQL/MariaDB data dump to SQLite-compatible SQL.
- Strips MySQL comments and ALTER TABLE ... KEYS statements.
- Replaces backticks with double quotes (SQLite identifier quoting).
Run from project root after migrations, then: sqlite3 db.sqlite3 < database_dump/dump_sqlite.sql
"""
import re
import sys
from pathlib import Path

def main():
    dump_path = Path(__file__).parent / "dump.sql"
    out_path = Path(__file__).parent / "dump_sqlite.sql"

    if len(sys.argv) >= 2:
        dump_path = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        out_path = Path(sys.argv[2])

    content = dump_path.read_text(encoding="utf-8", errors="replace")

    # Remove MySQL conditional comments /*! ... */ (multi-line)
    content = re.sub(r"/\*![\d ]+.*?\*/;?\s*", "", content, flags=re.DOTALL)
    # Line by line: drop MySQL-only lines
    lines = []
    for line in content.splitlines():
        s = line.strip()
        if s.startswith("/*!") or s.startswith("/*") and "*/" in s:
            continue
        if "ALTER TABLE" in s and ("DISABLE KEYS" in s or "ENABLE KEYS" in s):
            continue
        if s.startswith("SET ") and ("CHARACTER_SET" in s or "SQL_MODE" in s or "FOREIGN_KEY" in s or "NAMES" in s):
            continue
        lines.append(line)
    content = "\n".join(lines)

    # MySQL uses \' for a single quote inside strings; SQLite uses ''
    content = content.replace("\\'", "''")
    # Replace backticks with double quotes (SQLite identifier quoting)
    content = content.replace("`", '"')

    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote {out_path}")
    print("Next: sqlite3 db.sqlite3 < database_dump/dump_sqlite.sql")

if __name__ == "__main__":
    main()
