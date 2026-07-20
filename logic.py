#Importa do Banco de Dados
from database import conectar_db

#Import Biblioteca
import random

def buscar_jogadores_confirmados(data_jogo):
    """Busca os jogadores confirmados para uma semana específica"""
    conn = conectar_db()
    cursor = conn.cursor()

    #Query para buscar jogadores confirmados
    cursor.execute('''
        SELECT j.id, j.nome_jogador, j.posicao
        FROM jogadores j
        INNER JOIN confirmacoes c ON j.id = c.jogador_id
        WHERE c.data_jogo = ? AND c.confirmado = 1
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
    """Equilibra os times com base em posição e nota definida pelos admin"""

    #Calculando a nota de cada jogador
    jogadores_com_notas =[]
    for jogador_id, nome_jogador, posicao in jogadores:
        nota = calcular_nota_jogadores(jogador_id)
        jogadores_com_notas.append({
            'id':jogador_id,
            'nome':nome_jogador,
            'posicao':posicao,
            'nota':nota
        })

    #Ordenação das notas
    jogadores_com_notas.sort(key=lambda x: x['nota'], reverse=True)

    #Inicia os times
    times = {i: [] for i in range(1, num_times +1)}

    #Distribuição dos jogadores (draft)
    for idx, jogador in enumerate(jogadores_com_notas):
        time_num = (idx % num_times) +1
        times[time_num].append(jogador)

    return times

def validar_posicoes(times):
    """Valida se cada time tem as posições mínimas"""

    posicoes_esperadas = {
        'Goleiro': 1,
        'Zagueiro': 2,
        'Ala': 2,
        'Meia': 1,
        'Centroavante': 1
    }
    for num_time, jogadores in times.items():
        posicoes_time = {}

        #Mostra quantos de cada posição em cada time
        for jogador in jogadores:
            posicao = jogador ['posicao']
            posicoes_time[posicao] = posicoes_time.get(posicao, 0) +1
        
        #Verifica se tem as posições mínimas
        for posicao, qtde_minima in posicoes_esperadas.items():
            qtde_time = posicoes_time.get(posicao, 0)

            if qtde_time < qtde_minima:
                print (f"⚠️ Time {num_time} falta {qtde_minima - qtde_time} {posicao}(s)")
                return False

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

    #Passo 3: Verifica posições
    if not validar_posicoes(times):
        print("❌ Não foi possível preencher todas as posições")
        return False

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