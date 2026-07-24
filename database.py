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
    """Insere um novo jogador ou reativa um deletado"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Verifica se já existe (inativo)
    cursor.execute('SELECT id FROM jogadores WHERE nome_jogador = ?', (nome,))
    existe = cursor.fetchone()
    
    if existe:
        # Se existe mas tá inativo, ativa de novo
        cursor.execute('''
            UPDATE jogadores 
            SET ativo = 1 
            WHERE nome_jogador = ?
        ''', (nome,))
    else:
        # Se não existe, cria novo
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
    """Busca os jogadores confirmados (sem deletados, sem duplicatas)"""
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT DISTINCT j.id, j.nome_jogador, j.posicao
        FROM jogadores j
        INNER JOIN confirmacoes c ON j.id = c.jogador_id
        WHERE c.data_jogo = ? AND c.confirmado = 1 AND j.ativo = 1
        ORDER BY j.nome_jogador
    ''', (data_jogo,))

    jogadores = cursor.fetchall()
    conn.close()

    return jogadores
    
    # Remove duplicatas em Python também
    jogadores_unicos = []
    nomes_vistos = set()
    
    for j in jogadores:
        if j[1] not in nomes_vistos:
            jogadores_unicos.append(j)
            nomes_vistos.add(j[1])
    
    return jogadores_unicos

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

#ADMINS PODEM EXCLUIR JOGADORES
def deletar_jogador(jogador_id):
    """Deleta um jogador da lista"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE jogadores
        SET ativo = 0
        WHERE id = ?
    ''', (jogador_id,))
    
    conn.commit()
    conn.close()

def salvar_valor_futebol(valor):
    """Salva o valor padrão do futebol"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO configuracoes 
        (chave, valor, descricao)
        VALUES ('valor_futebol', ?, 'Valor padrão do futebol')
    ''', (str(valor),))
    
    conn.commit()
    conn.close()

def buscar_valor_futebol():
    """Busca o valor padrão do futebol"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT valor
        FROM configuracoes
        WHERE chave = 'valor_futebol'
    ''')
    
    resultado = cursor.fetchone()
    conn.close()
    
    if resultado:
        return float(resultado[0])
    else:
        return 100.0

def inserir_despesa(data_jogo, descricao, valor, admin_id):
    """Insere uma despesa"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO despesas 
        (data_jogo, descricao, valor, admin_id)
        VALUES (?, ?, ?, ?)
    ''', (data_jogo, descricao, valor, admin_id))
    
    conn.commit()
    conn.close()

def buscar_despesas(data_jogo):
    """Busca todas as despesas de uma data"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT descricao, valor, admin_id
        FROM despesas
        WHERE data_jogo = ?
        ORDER BY data_despesa DESC
    ''', (data_jogo,))
    
    despesas = cursor.fetchall()
    conn.close()
    
    return despesas

def inserir_marcacao(jogador_id, data_jogo, tipo):
    """Insere um gol ou assistência"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO marcacoes 
        (jogador_id, data_jogo, tipo)
        VALUES (?, ?, ?)
    ''', (jogador_id, data_jogo, tipo))
    
    conn.commit()
    conn.close()

def buscar_marcacoes(data_jogo):
    """Busca todas as marcações de uma data"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT j.nome_jogador, m.tipo, m.id
        FROM marcacoes m
        JOIN jogadores j ON m.jogador_id = j.id
        WHERE m.data_jogo = ?
        ORDER BY m.data_marcacao DESC
    ''', (data_jogo,))
    
    marcacoes = cursor.fetchall()
    conn.close()
    
    return marcacoes

def contar_marcacoes(data_jogo):
    """Conta gols e assistências por jogador"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT j.nome_jogador, 
               SUM(CASE WHEN m.tipo = 'gol' THEN 1 ELSE 0 END) as gols,
               SUM(CASE WHEN m.tipo = 'assistência' THEN 1 ELSE 0 END) as assistencias
        FROM marcacoes m
        JOIN jogadores j ON m.jogador_id = j.id
        WHERE m.data_jogo = ?
        GROUP BY j.nome_jogador
        ORDER BY gols DESC, assistencias DESC
    ''', (data_jogo,))
    
    stats = cursor.fetchall()
    conn.close()
    
    return stats

def deletar_marcacao(marcacao_id):
    """Deleta uma marcação"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM marcacoes
        WHERE id = ?
    ''', (marcacao_id,))
    
    conn.commit()
    conn.close()

def marcar_pagamento(jogador_id, data_jogo):
    """Marca que um jogador pagou - insere se não existe, atualiza se existe"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Primeiro tenta fazer update
    cursor.execute('''
        UPDATE confirmacoes
        SET pagou = 1
        WHERE jogador_id = ? AND data_jogo = ?
    ''', (jogador_id, data_jogo))
    
    # Se não atualizou nada, insere um novo
    if cursor.rowcount == 0:
        cursor.execute('''
            INSERT INTO confirmacoes 
            (jogador_id, data_jogo, confirmado, pagou)
            VALUES (?, ?, 1, 1)
        ''', (jogador_id, data_jogo))
    
    conn.commit()
    conn.close()

def desmarcar_pagamento(jogador_id, data_jogo):
    """Remove a marcação de pagamento"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE confirmacoes
        SET pagou = 0
        WHERE jogador_id = ? AND data_jogo = ?
    ''', (jogador_id, data_jogo))
    
    conn.commit()
    conn.close()

def contar_pagamentos(data_jogo):
    """Conta quantos pagaram e retorna lista (sem duplicatas)"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT j.nome_jogador, j.id
        FROM confirmacoes c
        JOIN jogadores j ON c.jogador_id = j.id
        WHERE c.data_jogo = ? AND c.pagou = 1 AND j.ativo = 1
        ORDER BY j.nome_jogador
    ''', (data_jogo,))
    
    pagamentos = cursor.fetchall()
    conn.close()
    
    return pagamentos

def total_pagamentos(data_jogo):
    """Retorna quantas pessoas pagaram (sem duplicatas)"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(DISTINCT jogador_id) FROM confirmacoes
        WHERE data_jogo = ? AND pagou = 1
    ''', (data_jogo,))
    
    resultado = cursor.fetchone()
    conn.close()
    
    return resultado[0] if resultado else 0

def calcular_saldo_por_data(data_jogo):
    """Calcula saldo de uma data específica (entrada - despesas)"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Total pagamentos
    cursor.execute('''
        SELECT COUNT(DISTINCT jogador_id) FROM confirmacoes
        WHERE data_jogo = ? AND pagou = 1
    ''', (data_jogo,))
    
    total_pag = cursor.fetchone()[0] or 0
    valor_futebol = buscar_valor_futebol()
    entrada = total_pag * valor_futebol
    
    # Total despesas
    cursor.execute('''
        SELECT SUM(valor) FROM despesas WHERE data_jogo = ?
    ''', (data_jogo,))
    
    despesa = cursor.fetchone()[0] or 0
    
    conn.close()
    
    saldo = entrada - despesa
    return {"entrada": entrada, "despesa": despesa, "saldo": saldo}

def calcular_saldo_total():
    """Calcula saldo total acumulado de todas as datas"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Total de todas as entradas (DISTINCT)
    cursor.execute('''
        SELECT COUNT(DISTINCT jogador_id) FROM confirmacoes
        WHERE pagou = 1
    ''')
    
    total_pag = cursor.fetchone()[0] or 0
    valor_futebol = buscar_valor_futebol()
    entrada_total = total_pag * valor_futebol
    
    # Total de todas as despesas
    cursor.execute('SELECT SUM(valor) FROM despesas')
    despesa_total = cursor.fetchone()[0] or 0
    
    conn.close()
    
    saldo_total = entrada_total - despesa_total
    return {"entrada": entrada_total, "despesa": despesa_total, "saldo": saldo_total}

def buscar_todas_datas():
    """Retorna todas as datas com movimentação"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT data_jogo FROM confirmacoes
        UNION
        SELECT DISTINCT data_jogo FROM despesas
        ORDER BY data_jogo DESC
    ''')
    
    datas = cursor.fetchall()
    conn.close()
    
    return [d[0] for d in datas]

def buscar_times_gerados(data_jogo):
    """Busca os times gerados para uma data (apenas jogadores ativos)"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT numero_time, jogador_id, j.nome_jogador, j.posicao
        FROM sorteio_semanal s
        JOIN jogadores j ON s.jogador_id = j.id
        WHERE s.data_jogo = ? AND j.ativo = 1
        ORDER BY numero_time, j.nome_jogador
    ''', (data_jogo,))
    
    times = cursor.fetchall()
    conn.close()
    
    return times

def contar_confirmados(data_jogo):
    """Conta quantos jogadores confirmaram"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(DISTINCT jogador_id)
        FROM confirmacoes
        WHERE data_jogo = ? AND confirmado = 1
    ''', (data_jogo,))
    
    resultado = cursor.fetchone()[0]
    conn.close()
    
    return resultado

def deletar_sorteio_anterior(data_jogo):
    """Deleta sorteios anteriores para esta data (para sobrescrever)"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM sorteio_semanal
        WHERE data_jogo = ?
    ''', (data_jogo,))
    
    conn.commit()
    conn.close()

def inserir_solicitacao_exclusao(marcacao_id, jogador_nome, tipo, data_jogo):
    """Insere uma solicitação de exclusão de marcação"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO solicitacoes_exclusao 
        (marcacao_id, jogador_nome, tipo, data_jogo, status)
        VALUES (?, ?, ?, ?, 'pendente')
    ''', (marcacao_id, jogador_nome, tipo, data_jogo))
    
    conn.commit()
    conn.close()

def buscar_solicitacoes_exclusao(data_jogo):
    """Busca solicitações pendentes"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, marcacao_id, jogador_nome, tipo
        FROM solicitacoes_exclusao
        WHERE data_jogo = ? AND status = 'pendente'
    ''', (data_jogo,))
    
    solicitacoes = cursor.fetchall()
    conn.close()
    
    return solicitacoes

def aprovar_solicitacao(solicitacao_id, marcacao_id):
    """Aprova e deleta a marcação"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM marcacoes WHERE id = ?', (marcacao_id,))
    cursor.execute('DELETE FROM solicitacoes_exclusao WHERE id = ?', (solicitacao_id,))
    
    conn.commit()
    conn.close()

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

    # TABELA SOLICITAÇÕES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitacoes_exclusao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marcacao_id INTEGER NOT NULL,
            jogador_nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            data_jogo DATE NOT NULL,
            status TEXT DEFAULT 'pendente',
            data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

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