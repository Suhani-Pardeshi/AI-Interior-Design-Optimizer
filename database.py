"""SQLite storage for saved CasaCraft projects."""
import json, sqlite3
from config import DATABASE_PATH

def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, room TEXT, style TEXT, budget REAL, area REAL, details TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()

def save_project(name, room, style, budget, area, details=None):
    init_db()
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("INSERT INTO projects (name, room, style, budget, area, details) VALUES (?, ?, ?, ?, ?, ?)", (str(name), str(room), str(style), float(budget or 0), float(area or 0), json.dumps(details or {}, ensure_ascii=False, default=str)))
        conn.commit()

def get_projects():
    init_db()
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    result=[]
    for row in rows:
        item=dict(row)
        try: item["details"]=json.loads(item.get("details") or "{}")
        except Exception: item["details"]={}
        result.append(item)
    return result
