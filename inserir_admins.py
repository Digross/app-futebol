from database import ADMINS_TOKENS, conectar_db

conn = conectar_db()
cursor = conn.cursor()

for token, nome in ADMINS_TOKENS:
    cursor.execute('INSERT OR IGNORE INTO admins (token, nome_admin) VALUES (?, ?)', (token, nome))

conn.commit()
conn.close()

print('✅ Admins inseridos com sucesso!')