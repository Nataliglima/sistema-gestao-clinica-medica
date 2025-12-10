print(">>> ARQUIVO ver_db.py EXECUTADO <<<")

import sqlite3

conn = sqlite3.connect("healthapi.db")
cur = conn.cursor()

try:
    print("\n=== TABELAS ===")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cur.fetchall())

    print("\n=== USUÁRIOS ===")
    cur.execute("SELECT * FROM usuarios;")
    usuarios = cur.fetchall()
    print("TOTAL:", len(usuarios))
    for u in usuarios:
        print(u)

except Exception as e:
    print("ERRO:", e)

conn.close()

