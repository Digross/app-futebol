#Importa do Banco de Dados
from database import conectar_db

#Import Biblioteca
import random

def buscar_jogadores_confirmados(data_jogo):
    """Busca os jogadores confirmados para uma semana específica (sem duplicatas)"""
    conn = conectar_db()
    cursor = conn.cursor()

    #Query para buscar jogadores confirmados (DISTINCT)
    cursor.execute('''
        SELECT DISTINCT j.id, j.nome_jogador, j.posicao
        FROM jogadores j
        INNER JOIN confirmacoes c ON j.id = c.jogador_id
        WHERE c.data_jogo = ? AND c.confirmado = 1
        ORDER BY j.nome_jogador
        ''', (data_jogo,))

    jogadores = cursor.fetchall()
    conn.close()

    return jogadores

def calcular_nota_jogadores(jogador_id):
    """Calcula a nota média de cada jogador
    Cada admin atribui uma nota para fazer a média"""
    conn = conectar_db()
    cursor = conn.cursor()

    #Query para buscar as notas
    cursor.execute('''
        SELECT nota
        FROM notas_jogadores
        WHERE jogador_id = ?
    ''',(jogador_id,)
        )

    notas = cursor.fetchall()
    conn.close()

    #Caso não exista no (retorna 0)
    if not notas:
        return 0

    #Cálculo da média
    soma_notas = sum([nota[0] for nota in notas])
    media = soma_notas / len(notas)

    return media

def equilibrar_times(jogadores, num_times=3):
    """Cria EXATAMENTE num_times com 7 cada, sobra em time extra"""
    
    import random

    jogadores_com_notas = []
    for jogador_id, nome_jogador, posicao in jogadores:
        nota = calcular_nota_jogadores(jogador_id)
        jogadores_com_notas.append({
            'id': jogador_id,
            'nome': nome_jogador,
            'posicao': posicao,
            'nota': nota
        })

    random.shuffle(jogadores_com_notas)

    times = {}
    total_por_time = 7
    idx = 0
    
    # Cria EXATAMENTE num_times com 7 cada
    for num_time in range(1, num_times + 1):
        times[num_time] = jogadores_com_notas[idx:idx+total_por_time]
        idx += total_por_time
    
    # Sobra em time extra
    if idx < len(jogadores_com_notas):
        times[num_times + 1] = jogadores_com_notas[idx:]
    
    return times


def validar_posicoes(times):
    """Apenas valida que tem jogadores"""
    return True

def gerar_sorteio(data_jogo, num_times=3):
    """Função que juntas as lógicas acima
    1. Busca jogadores confirmados
    2.Equilibra os times
    3.Verifica posicoes
    4. Salva no Bando de Dados"""

    #Passo 1: Busca Jogadores confirmados
    jogadores = buscar_jogadores_confirmados(data_jogo)
    if not jogadores:
        print("❌ Nenhum jogador confirmado para essa semana!")
        return False

    #Passo 2: Equilibrio dos times
    times = equilibrar_times(jogadores, num_times)

    #Passo 4: Salva infos acima no Banco de Dados
    conn = conectar_db()
    cursor = conn.cursor()

    for num_time, jogadores_time in times.items():
        for jogador in jogadores_time:
            cursor.execute('''
            INSERT INTO sorteio_semanal
            (data_jogo, numero_time, jogador_id, posicao)
            VALUES (?, ?, ?, ?)
            ''',(data_jogo, num_time, jogador['id'], jogador['posicao'])
            )
    conn.commit()
    conn.close()

    print(f"✅ Sorteio gerado com sucesso para semana {data_jogo}!")
    return True