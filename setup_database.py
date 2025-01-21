import sqlite3

def setup_database():
    conn = sqlite3.connect("normas_sst.db")  # Este archivo será tu base de datos
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS normas (
                        id INTEGER PRIMARY KEY,
                        titulo TEXT,
                        enlace TEXT
                    )""")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
    print("Base de datos creada y configurada correctamente.")
