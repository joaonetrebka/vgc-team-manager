import sqlite3

def criar_banco():
    conexao = sqlite3.connect("vgc.db")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            formato TEXT NOT NULL,
            id_usuario INTEGER NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pokemons_do_time (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_time INTEGER NOT NULL,
            especie TEXT NOT NULL,
            item TEXT,
            habilidade TEXT,
            natureza TEXT,
            tera_type TEXT,
            golpe1 TEXT,
            golpe2 TEXT,
            golpe3 TEXT,
            golpe4 TEXT,
            FOREIGN KEY (id_time) REFERENCES times(id)
        )
    """)

    conexao.commit()
    conexao.close()
    print("Banco criado com sucesso!")

if __name__ == "__main__":
    criar_banco()