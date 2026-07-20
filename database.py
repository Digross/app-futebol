import sqlite3
from pathlib import Path

# Caminho do banco
DB_PATH = Path(__file__).parent / "banco.db"
DB_VERSION = 1

# Tokens dos admins
ADMINS_TOKENS = [
    ("Corinthians1910", "Dilson"),
    ("Santástico", "Gustavo"),
    ("1910SCCP", "Viana"),
    ("TricolorSP", "Binha"),
    ("Neymar2030", "Allan"),
    ("Coringão", "Thiago")
]

def conectar_db():
    """Abre conexão com o banco de dados"""
    conn = sqlite3.connect(str(DB_PATH))
    return conn

def buscar_todos_jogadores():
    """Retorna lista de TODOS os jogadores cadastrados"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome_jogador, posicao
        FROM jogadores
        WHERE ativo = 1
        ORDER BY nome_jogador
    ''')
    
    jogadores = cursor.fetchall()
    conn.close()
    
    return jogadores

def inserir_jogador(nome, posicao):
    """Insere um novo jogador"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO jogadores (nome_jogador, posicao, ativo)
        VALUES (?, ?, 1)
    ''', (nome, posicao))
    
    conn.commit()
    conn.close()

def inserir_confirmacao(jogador_id, data_jogo):
    """Registra que um jogador confirmou presença"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO confirmacoes 
        (jogador_id, data_jogo, confirmado, pagou)
        VALUES (?, ?, 1, 0)
    ''', (jogador_id, data_jogo))
    
    conn.commit()
    conn.close()

def buscar_jogadores_confirmados(data_jogo):
    """Busca os jogadores confirmados para uma data"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT j.id, j.nome_jogador, j.posicao
        FROM jogadores j
        INNER JOIN confirmacoes c ON j.id = c.jogador_id
        WHERE c.data_jogo = ? AND c.confirmado = 1
    ''', (data_jogo,))
    
    jogadores = cursor.fetchall()
    conn.close()
    
    return jogadores

def salvar_nota_jogador(jogador_id, admin_id, nota):
    """Salva a nota de um jogador por um admin"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM notas_jogadores
        WHERE jogador_id = ? AND admin_id = ?
    ''', (jogador_id, admin_id))
    
    cursor.execute('''
        INSERT INTO notas_jogadores 
        (jogador_id, admin_id, nota)
        VALUES (?, ?, ?)
    ''', (jogador_id, admin_id, nota))
    
    conn.commit()
    conn.close()

def buscar_notas_por_jogador(jogador_id):
    """Retorna notas de um jogador dadas por cada admin"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.nome_admin, n.nota
        FROM notas_jogadores n
        JOIN admins a ON n.admin_id = a.id
        WHERE n.jogador_id = ?
        ORDER BY a.nome_admin
    ''', (jogador_id,))
    
    notas = cursor.fetchall()
    conn.close()
    
    return notas

def verificar_token_admin(token):
    """Verifica se o token é válido e retorna (id, nome) ou None"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome_admin
        FROM admins
        WHERE token = ?
    ''', (token,))
    
    resultado = cursor.fetchone()
    conn.close()
    
    return resultado

def salvar_data_jogo_atual(data_jogo):
    """Salva qual é a data do jogo atual"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO configuracoes 
        (chave, valor, descricao)
        VALUES ('data_jogo_atual', ?, 'Data do próximo jogo')
    ''', (str(data_jogo),))
    
    conn.commit()
    conn.close()

def buscar_data_jogo_atual():
    """Busca qual é a data do jogo atual definida pelos admins"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT valor
        FROM configuracoes
        WHERE chave = 'data_jogo_atual'
    ''')
    
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return resultado[0]
    else:
        return None

def iniciar_banco():
    """Cria as tabelas se não existirem e verifica versão"""
    
    version_file = Path(__file__).parent / ".db_version"
    
    # Se a versão mudou, deleta o banco antigo
    if version_file.exists():
        with open(version_file, 'r') as f:
            conteudo = f.read().strip()
            if conteudo:
                versao_atual = int(conteudo)
            else:
                versao_atual = 0
        
        if versao_atual != DB_VERSION:
            if DB_PATH.exists():
                DB_PATH.unlink()
                print(f"🔄 Banco desatualizado. Recriando v{DB_VERSION}...")
    
    # Cria o banco novo
    conn = conectar_db()
    cursor = conn.cursor()

    #TABELA JOGADORES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_jogador TEXT NOT NULL UNIQUE,
            posicao TEXT NOT NULL,
            ativo BOOLEAN DEFAULT 1
        )
    ''')

    #TABELA ADMINS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL UNIQUE,
            nome_admin TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    #TABELA SEMANAS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS semanas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_jogo DATE NOT NULL UNIQUE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    #TABELA CONFIRMAÇÃO
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS confirmacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jogador_id INTEGER NOT NULL,
            data_jogo DATE NOT NULL,
            confirmado BOOLEAN DEFAULT 0,
            pagou BOOLEAN DEFAULT 0,
            FOREIGN KEY (jogador_id) REFERENCES jogadores(id),
            FOREIGN KEY (data_jogo) REFERENCES semanas(data_jogo)
        ) 
    ''')

    #TABELA NOTAS_JOGADORES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas_jogadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jogador_id INTEGER NOT NULL,
            admin_id INTEGER NOT NULL,
            nota INTEGER NOT NULL,
            data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (jogador_id) REFERENCES jogadores(id),
            FOREIGN KEY (admin_id) REFERENCES admins(id)
        )
    ''')

    #TABELA MARCAÇÕES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marcacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jogador_id INTEGER NOT NULL,
            data_jogo DATE NOT NULL,
            tipo TEXT NOT NULL,
            data_marcacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (jogador_id) REFERENCES jogadores(id),
            FOREIGN KEY (data_jogo) REFERENCES semanas(data_jogo)
        )
    ''')

    #TABELA SORTEIO_SEMANAL
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sorteio_semanal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_jogo DATE NOT NULL,
            numero_time INTEGER NOT NULL,
            jogador_id INTEGER NOT NULL,
            posicao TEXT NOT NULL,
            data_sorteio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (data_jogo) REFERENCES semanas(data_jogo),
            FOREIGN KEY (jogador_id) REFERENCES jogadores(id)
        )
    ''')

    #TABELA DESPESAS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_jogo DATE NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_despesa TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            admin_id INTEGER NOT NULL,
            FOREIGN KEY (admin_id) REFERENCES admins(id),
            FOREIGN KEY (data_jogo) REFERENCES semanas(data_jogo)
        )
    ''')

    #TABELA CONFIGURAÇÕES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT NOT NULL UNIQUE,
            valor TEXT NOT NULL,
            descricao TEXT,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Insere os admins
    conn = conectar_db()
    cursor = conn.cursor()
    
    for token, nome in ADMINS_TOKENS:
        cursor.execute('''
            INSERT OR IGNORE INTO admins (token, nome_admin)
            VALUES (?, ?)
        ''', (token, nome))
    
    conn.commit()
    conn.close()
    
    # Salva a versão
    with open(version_file, 'w') as f:
        f.write(str(DB_VERSION))
    
    print("✅ Banco de dados inicializado com sucesso!")