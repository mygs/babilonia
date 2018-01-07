import sqlite3

conn = sqlite3.connect('nodes.db')
cursor = conn.cursor()

# lendo os dados
cursor.execute("""
SELECT * FROM NODECONF;
""")

for linha in cursor.fetchall():
    print(linha)


conn.close()
