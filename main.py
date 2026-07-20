import streamlit as st
from database import (
    conectar_db, iniciar_banco, salvar_data_jogo_atual, buscar_data_jogo_atual,
    buscar_todos_jogadores, inserir_jogador, inserir_confirmacao,
    salvar_nota_jogador, buscar_notas_por_jogador
)
from logic import (
    buscar_jogadores_confirmados,
    calcular_nota_jogadores,
    gerar_sorteio
)
import pandas as pd

# Inicia o Banco de Dados
iniciar_banco()

st.set_page_config(page_title="BOLA Y BRASA", layout="wide")
st.title("⚽ BOLA Y BRASA")

aba1, aba2, aba3 = st.tabs(["✅ Confirmação", "⚽ Marcador", "🎲 Sorteio"])

# ===================== ABA 1: CONFIRMAÇÃO =====================
with aba1:
    st.header("Confirme sua Presença!")
    
    data_jogo = buscar_data_jogo_atual()
    
    if data_jogo:
        st.info(f"📅 Próximo jogo: {data_jogo}")
        
        st.subheader("Você já jogou conosco antes?")
        
        # Opção 1: Jogador existente
        jogadores_existentes = buscar_todos_jogadores()
        if jogadores_existentes:
            nomes_existentes = [f"{j[1]}" for j in jogadores_existentes]
            jogador_existente = st.selectbox(
                "Selecione seu nome:",
                ["-- Selecione --"] + nomes_existentes
            )
            
            if jogador_existente != "-- Selecione --":
                # Pega o ID do jogador selecionado
                jogador_id = next(j[0] for j in jogadores_existentes if j[1] == jogador_existente)
                
                if st.button("✅ Confirmar Presença"):
                    inserir_confirmacao(jogador_id, data_jogo)
                    st.success(f"Presença confirmada para {jogador_existente}!")
        
        st.divider()
        
        # Opção 2: Novo jogador
        st.subheader("➕ Novo Jogador")
        
        nome_completo = st.text_input("Nome completo:")
        nova_posicao = st.selectbox(
            "Sua posição:",
            ["Goleiro", "Zagueiro", "Ala", "Meia", "CentroAvante"]
        )
        
        if st.button("✅ Confirmar Presença (Novo)"):
            if nome_completo:
                nome_completo = f"{novo_nome} {novo_sobrenome}"
                inserir_jogador(nome_completo, nova_posicao)
                
                # Busca o ID do jogador que acabou de ser criado
                jogadores = buscar_todos_jogadores()
                jogador_id = next(j[0] for j in jogadores if j[1] == nome_completo)
                
                inserir_confirmacao(jogador_id, data_jogo)
                st.success(f"Bem-vindo, {nome_completo}! Presença confirmada!")
            else:
                st.error("Preencha nome e sobrenome!")
    else:
        st.warning("⚠️ Nenhuma data definida ainda pelos admins")


# ===================== ABA 2: MARCADOR =====================
with aba2:
    st.header("⚽ Marcador de Gols e Assistências")
    
    data_jogo = buscar_data_jogo_atual()
    
    if data_jogo:
        st.info(f"📅 Data do jogo: {data_jogo}")
        
        jogadores = buscar_jogadores_confirmados(data_jogo)
        
        if jogadores:
            nomes_jogadores = [j[1] for j in jogadores]
            jogador_selecionado = st.selectbox("Selecione o jogador:", nomes_jogadores)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("⚽ Marcar Gol"):
                    st.success(f"{jogador_selecionado} marcou um GOL!")
            
            with col2:
                if st.button("🎯 Marcar Assistência"):
                    st.success(f"{jogador_selecionado} deu uma ASSISTÊNCIA!")
        else:
            st.info("Nenhum jogador confirmado para essa data")
    else:
        st.warning("⚠️ Nenhuma data definida ainda pelos admins")


# ===================== ABA 3: SORTEIO (ADMIN) =====================
with aba3:
    st.header("🎲 Sorteio de Times - ADMIN")
    
    # Usar session_state para manter login
    if 'admin_autenticado' not in st.session_state:
        st.session_state.admin_autenticado = False
        st.session_state.admin_id = None
    
    if not st.session_state.admin_autenticado:
        # Autenticação por token
        token_admin = st.text_input("Digite seu token de admin:", type="password", key="token_input")
        
        if st.button("Verificar acesso"):
            from database import verificar_token_admin
            resultado = verificar_token_admin(token_admin)
            
            if resultado:
                admin_id, admin_nome = resultado
                st.session_state.admin_autenticado = True
                st.session_state.admin_id = admin_id
                st.session_state.admin_nome = admin_nome
                st.rerun()
            else:
                st.error("❌ Token inválido!")
    
    else:
        # Admin autenticado
        st.success(f"✅ Acesso de admin confirmado! Bem-vindo, {st.session_state.admin_nome}")
        
        if st.button("Sair"):
            st.session_state.admin_autenticado = False
            st.rerun()
        
        # Subabas dentro do Sorteio
        subaba1, subaba2 = st.tabs(["Gerar Sorteio", "Financeiro"])
        
        # --- SUBABA: GERAR SORTEIO ---
        with subaba1:
            st.subheader("Gerar Sorteio")
            
            data_sorteio = st.date_input("Defina a data do próximo jogo:")
            
            if st.button("💾 Salvar Data"):
                salvar_data_jogo_atual(data_sorteio)
                st.success(f"✅ Data definida para {data_sorteio}")
            
            st.divider()
            
            # Seção de atribuição de notas
            st.subheader("Atribuir Notas aos Jogadores")
            
            jogadores_confirmados = buscar_jogadores_confirmados(str(data_sorteio))
            
            if jogadores_confirmados:
                # Cria um dicionário para armazenar as notas
                notas_dict = {}
                
                st.write("Preencha as notas de 1 a 10:")
                
                for jogador_id, nome, posicao in jogadores_confirmados:
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"{nome} ({posicao})")
                    
                    with col2:
                        nota = st.number_input(
                            "Nota:",
                            min_value=1,
                            max_value=10,
                            value=5,
                            key=f"nota_{jogador_id}"
                        )
                        notas_dict[jogador_id] = nota
                
                if st.button("💾 Salvar Notas"):
                    for jogador_id, nota in notas_dict.items():
                        salvar_nota_jogador(jogador_id, st.session_state.admin_id, nota)
                    st.success("✅ Notas salvas com sucesso!")
            else:
                st.info("Nenhum jogador confirmado para essa data ainda")
            
            st.divider()
            
            num_times = st.number_input("Número de times:", min_value=2, max_value=5, value=3)
            
            if st.button("🎲 Gerar Sorteio"):
                resultado = gerar_sorteio(str(data_sorteio), num_times)
                if resultado:
                    st.success("✅ Sorteio gerado com sucesso!")
                else:
                    st.error("❌ Erro ao gerar sorteio")
        
        # --- SUBABA: FINANCEIRO ---
        with subaba2:
            st.subheader("Controle Financeiro")
            
            col1, col2 = st.columns(2)
            
            with col1:
                valor_futebol = st.number_input("Valor do futebol (R$):", min_value=0.0, value=100.0)
                st.info(f"Cada jogador paga: R$ {valor_futebol:.2f}")
            
            with col2:
                despesa_desc = st.text_input("Descrição da despesa (ex: Quadra, Bola):")
                despesa_valor = st.number_input("Valor da despesa (R$):", min_value=0.0)
                
                if st.button("➕ Adicionar Despesa"):
                    if despesa_desc and despesa_valor > 0:
                        st.success(f"Despesa '{despesa_desc}' adicionada!")
                    else:
                        st.error("Preencha todos os campos")