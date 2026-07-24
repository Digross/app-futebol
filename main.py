import streamlit as st
from database import (
    conectar_db, iniciar_banco, salvar_data_jogo_atual, buscar_data_jogo_atual,
    buscar_todos_jogadores, inserir_jogador, inserir_confirmacao,
    salvar_nota_jogador, buscar_notas_por_jogador, verificar_token_admin,
    buscar_jogadores_confirmados, deletar_jogador, marcar_pagamento,
    desmarcar_pagamento, contar_pagamentos, total_pagamentos, inserir_despesa,
    buscar_despesas, calcular_saldo_por_data, calcular_saldo_total,
    buscar_todas_datas, deletar_sorteio_anterior,
    buscar_times_gerados, contar_confirmados, contar_marcacoes, buscar_marcacoes,
    deletar_marcacao, inserir_marcacao
)
from logic import (
    calcular_nota_jogadores,
    gerar_sorteio
)
import pandas as pd
from datetime import datetime

iniciar_banco()

# CORES
CORES = {
    "azul_escuro": "#06111D",
    "dourado": "#2F388C", #botões
    "branco": "#FFFFFF",
    "vermelho": "#79A1E5" #destaque data
}

# CONFIG PAGE
st.set_page_config(page_title="BOLA Y BRASA", layout="wide", initial_sidebar_state="collapsed")

# ESTILO ÚNICO - TUDO JUNTO
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(135deg, {CORES['azul_escuro']} 0%, #1a4d7a 100%);
    }}
    
    h1, h2, h3 {{
        color: {CORES['dourado']};
        font-weight: bold;
    }}
    
    .stButton > button {{
        background-color: {CORES['dourado']};
        color: {CORES['azul_escuro']};
        border-radius: 15px;
        border: none;
        font-weight: bold;
        padding: 12px 24px;
    }}
    
    .stButton > button:hover {{
        background-color: {CORES['vermelho']};
        color: {CORES['branco']};
    }}
    
    .stMetric {{
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 15px;
        border-left: 4px solid {CORES['dourado']};
    }}
</style>
""", unsafe_allow_html=True)

# HEADER - LOGO
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image("brasao.png", width=80)

st.divider()

# ABAS
aba1, aba2, aba3 = st.tabs(["✅ Confirmação", "⚽ Marcador", "🎲 Sorteio"])

# ===================== ABA 1: CONFIRMAÇÃO =====================
with aba1:
    st.markdown(f"<h2 style='text-align: center;'>Confirme sua Presença!</h2>", unsafe_allow_html=True)
    
    try:
        data_jogo = buscar_data_jogo_atual()
        
        if not data_jogo:
            st.warning("⚠️ Nenhuma data definida pelos admins")
        else:
            # DATA GRANDE E VISÍVEL
            from datetime import datetime
            data_formatada = datetime.strptime(str(data_jogo), "%Y-%m-%d").strftime("%d/%m/%Y")
            st.markdown(f"""
                <div style='background: {CORES['vermelho']}; padding: 20px; border-radius: 15px; text-align: center;'>
                    <h3 style='color: {CORES['branco']}; margin: 0;'>📅 Próximo Futebol</h3>
                    <p style='color: {CORES['dourado']}; font-size: 28px; font-weight: bold; margin: 10px 0;'>{data_formatada}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # SEÇÃO 1: CONFIRMAÇÃO PRESENÇA
            st.subheader("✅ Já Jogou Conosco?")
            jogadores_existentes = buscar_todos_jogadores()
            
            if jogadores_existentes:
                nomes = [j[1] for j in jogadores_existentes]
                selecionado = st.selectbox(
                    "Selecione seu nome:",
                    nomes,
                    key="conf_exist",
                    index=None,
                    placeholder="🔍 Procure seu nome..."
                )
                
                if selecionado:
                    if st.button("✅ Confirmar Presença", key="btn_conf_exist"):
                        jog_id = next(j[0] for j in jogadores_existentes if j[1] == selecionado)
                        inserir_confirmacao(jog_id, data_jogo)
                        st.success(f"✅ Presença confirmada para {selecionado}!")
                        st.balloons()
            
            st.divider()
            
            # SEÇÃO 2: NOVO JOGADOR
            st.subheader("➕ Novo Jogador")
            nome = st.text_input("Seu nome:", placeholder="Digite seu nome completo")
            pos = st.selectbox(
                "Posição:",
                ["Goleiro", "Zagueiro", "Ala", "Meia", "CentroAvante"],
                key="conf_pos",
                index=None,
                placeholder="Selecione sua posição"
            )
            
            if st.button("✅ Confirmar (Novo)", key="btn_conf_novo"):
                if nome:
                    inserir_jogador(nome, pos)
                    jogadores = buscar_todos_jogadores()
                    jog_id = next(j[0] for j in jogadores if j[1] == nome)
                    inserir_confirmacao(jog_id, data_jogo)
                    st.success(f"✅ Bem-vindo, {nome}!")
                    st.balloons()
            
            st.divider()
            
            # SEÇÃO 3: CONFIRMAR PAGAMENTO
            st.subheader("💳 Confirmar Pagamento")
            jogadores_existentes = buscar_todos_jogadores()
            if jogadores_existentes:
                nomes = [j[1] for j in jogadores_existentes]
                selecionado_pag = st.selectbox(
                    "Seu nome:",
                    nomes,
                    key="pag_nome",
                    index=None,
                    placeholder="🔍 Procure seu nome..."
                )
                
                if selecionado_pag:
                    if st.button("💳 Confirmar Pagamento", key="btn_pag_conf"):
                        jog_id = next(j[0] for j in jogadores_existentes if j[1] == selecionado_pag)
                        marcar_pagamento(jog_id, data_jogo)
                        st.success(f"✅ Pagamento confirmado!")
    
    except Exception as e:
        st.error(f"Erro: {str(e)}")


# ===================== ABA 2: MARCADOR =====================
with aba2:
    st.markdown(f"<h2 style='text-align: center;'>⚽ Marcador de Gols</h2>", unsafe_allow_html=True)
    
    try:
        data_jogo = buscar_data_jogo_atual()
        
        if data_jogo:
            st.info(f"📅 Data: {data_jogo}")
            
            jogadores = buscar_jogadores_confirmados(data_jogo)
            
            if jogadores:
                nomes_jogadores = [j[1] for j in jogadores]
                
                st.subheader("⚽ Registrar Gol e Assistência")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**⚽ Quem fez o gol?**")
                    jogador_gol = st.selectbox(
                        "Selecione (obrigatório):",
                        nomes_jogadores,
                        key="marcador_gol",
                        index=None,
                        placeholder="🔍 Procure..."
                    )
                
                with col2:
                    st.write("**🎯 Quem deu a assistência?**")
                    jogador_assist = st.selectbox(
                        "Selecione (opcional):",
                        nomes_jogadores,
                        key="marcador_assist",
                        index=None,
                        placeholder="🔍 Procure..."
                    )
                
                if st.button("📝 Registrar Jogada", key="btn_registrar_jogada"):
                    if not jogador_gol:
                        st.error("❌ Selecione quem fez o gol!")
                    else:
                        jogador_gol_id = next(j[0] for j in jogadores if j[1] == jogador_gol)
                        inserir_marcacao(jogador_gol_id, data_jogo, "gol")
                        
                        if jogador_assist:
                            jogador_assist_id = next(j[0] for j in jogadores if j[1] == jogador_assist)
                            inserir_marcacao(jogador_assist_id, data_jogo, "assistência")
                            st.success(f"⚽ {jogador_gol} marcou! 🎯 {jogador_assist} assistiu!")
                        else:
                            st.success(f"⚽ {jogador_gol} marcou!")
                        
                        st.rerun()
                
                st.divider()
                
                # TABELA DE RANKING
                st.subheader("🏆 Ranking do Jogo")
                
                stats = contar_marcacoes(data_jogo)
                
                if stats:
                    df_stats = []
                    for nome, gols, assists in stats:
                        gols = gols or 0
                        assists = assists or 0
                        df_stats.append({
                            "Nome": nome,
                            "⚽ Gols": gols,
                            "🎯 Assistências": assists
                        })
                    
                    df = pd.DataFrame(df_stats)
                    df = df.sort_values(by=["⚽ Gols", "🎯 Assistências"], ascending=False).reset_index(drop=True)
                    df.index = df.index + 1
                    
                    st.dataframe(df, width='stretch')
                else:
                    st.info("Nenhuma marcação ainda")
                
                st.divider()
                
                # SOLICITAR EXCLUSÃO
                st.subheader("🗑️ Solicitar Exclusão de Marcação")
                
                marcacoes = buscar_marcacoes(data_jogo)
                
                if marcacoes:
                    st.write("**Clique para solicitar exclusão:**")
                    for nome, tipo, marcacao_id in marcacoes:
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            icone = "⚽" if tipo == "gol" else "🎯"
                            st.write(f"{icone} {nome} - {tipo.upper()}")
                        
                        with col2:
                            if st.button("❌", key=f"solicitar_{marcacao_id}"):
                                st.info("✅ Solicitação enviada ao admin!")
                else:
                    st.info("Nenhuma marcação registrada")
            else:
                st.info("Nenhum jogador confirmado para essa data")
        else:
            st.warning("⚠️ Nenhuma data definida pelos admins")
    
    except Exception as e:
        st.error(f"Erro: {str(e)}")


# ===================== ABA 3: SORTEIO (ADMIN) =====================
with aba3:
    st.markdown(f"<h2 style='text-align: center;'>🎲 Sorteio de Times - ADMIN</h2>", unsafe_allow_html=True)
    
    if 'admin_autenticado' not in st.session_state:
        st.session_state.admin_autenticado = False
        st.session_state.admin_id = None
    
    if not st.session_state.admin_autenticado:
        token_admin = st.text_input("Digite seu token de admin:", type="password", key="token_input")
        
        if st.button("Verificar acesso"):
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
        st.success(f"✅ {st.session_state.admin_nome}")
        
        if st.button("Sair"):
            st.session_state.admin_autenticado = False
            st.rerun()
        
        subaba1, subaba2 = st.tabs(["Gerar Sorteio", "Financeiro"])
        
        # --- SUBABA: GERAR SORTEIO ---
        with subaba1:
            st.subheader("Gerar Sorteio")
            
            data_sorteio = st.date_input("Defina a data do próximo jogo:")
            
            if st.button("💾 Salvar Data"):
                salvar_data_jogo_atual(data_sorteio)
                st.success(f"✅ Data definida para {data_sorteio}")
            
            st.divider()
            
           # TOTAL DE JOGADORES CONFIRMADOS
            jogadores_confirmados = buscar_jogadores_confirmados(str(data_sorteio))
            total_confirmados = len(jogadores_confirmados)
            st.markdown(f"""
            <div style='background: {CORES['dourado']}; padding: 15px; border-radius: 10px; text-align: center;'>
                <p style='color: {CORES['azul_escuro']}; font-size: 18px; font-weight: bold; margin: 0;'>
                    👥 Jogadores Confirmados: <span style='font-size: 24px;'>{total_confirmados}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            
            # Atribuir notas
            st.subheader("Atribuir Notas aos Jogadores")
            
            jogadores_confirmados = buscar_jogadores_confirmados(str(data_sorteio))
            
            if jogadores_confirmados:
                notas_dict = {}
                
                st.write("Preencha as notas de 1 a 10:")
                
                for idx, (jogador_id, nome, posicao) in enumerate(jogadores_confirmados):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"{nome} ({posicao})")
                    
                    with col2:
                        nota = st.number_input(
                            "Nota:",
                            min_value=1,
                            max_value=10,
                            value=5,
                            key=f"nota_gerar_{idx}_{jogador_id}"
                        )
                        notas_dict[jogador_id] = nota
                
                if st.button("💾 Salvar Notas"):
                    for jogador_id, nota in notas_dict.items():
                        salvar_nota_jogador(jogador_id, st.session_state.admin_id, nota)
                    st.success("✅ Notas salvas!")
            else:
                st.info("Nenhum jogador confirmado para essa data ainda")
            
            st.divider()
            
            num_times = st.number_input("Número de times:", min_value=1, max_value=5, value=3)


            if st.button("🗑️ Deletar Sorteio Anterior"):
                from database import deletar_sorteio_anterior
                deletar_sorteio_anterior(str(data_sorteio))
                st.success("✅ Sorteio deletado!")
                st.rerun()
            
            if st.button("🎲 Gerar Sorteio"):
                from database import deletar_sorteio_anterior
                deletar_sorteio_anterior(str(data_sorteio))
                resultado = gerar_sorteio(str(data_sorteio), int(num_times))
                if resultado:
                    st.success("✅ Sorteio gerado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao gerar sorteio")
            
            # Mostrar times gerados
            st.divider()
            st.subheader("⚽ Times Gerados")
            
            times_gerados = buscar_times_gerados(str(data_sorteio))
            
            if times_gerados:
                times_dict = {}
                for numero_time, jogador_id, nome, posicao in times_gerados:
                    if numero_time not in times_dict:
                        times_dict[numero_time] = []
                    times_dict[numero_time].append({"nome": nome, "posicao": posicao})
                
                for numero_time in sorted(times_dict.keys()):
                    st.write(f"**⚽ TIME {numero_time}** ({len(times_dict[numero_time])} jogadores)")
                    
                    df_time = []
                    for i, jogador in enumerate(times_dict[numero_time], 1):
                        df_time.append({"#": i, "Nome": jogador["nome"], "Posição": jogador["posicao"]})
                    
                    df = pd.DataFrame(df_time)
                    st.dataframe(df, width='stretch')
                    st.write("")
            else:
                st.info("Nenhum sorteio gerado ainda")
            
            st.divider()
            
            # DELETAR MARCAÇÕES
            st.subheader("🗑️ Deletar Marcações do Jogo")
            
            marcacoes = buscar_marcacoes(str(data_sorteio))
            
            if marcacoes:
                for nome, tipo, marcacao_id in marcacoes:
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        icone = "⚽" if tipo == "gol" else "🎯"
                        st.write(f"{icone} {nome} - {tipo.upper()}")
                    
                    with col2:
                        if st.button("❌", key=f"del_marca_{marcacao_id}"):
                            deletar_marcacao(marcacao_id)
                            st.success("Marcação deletada!")
                            st.rerun()
            else:
                st.info("Nenhuma marcação registrada")
            
            st.divider()
            
            # Gerenciar jogadores
            st.subheader("❌ Gerenciar Jogadores")
            
            todos_jogadores = buscar_todos_jogadores()
            
            if todos_jogadores:
                nomes_jogadores = [j[1] for j in todos_jogadores]
                jogador_deletar = st.selectbox(
                    "Selecione jogador para remover:",
                    nomes_jogadores,
                    key="deletar_jogador",
                    index=None,
                    placeholder="🔍 Procure o jogador..."
                )
                
                if jogador_deletar:
                    if st.button("🗑️ Remover Jogador", key="btn_deletar"):
                        jogador_id = next(j[0] for j in todos_jogadores if j[1] == jogador_deletar)
                        deletar_jogador(jogador_id)
                        st.success(f"Jogador '{jogador_deletar}' removido!")
                        st.rerun()
        
        # --- SUBABA: FINANCEIRO ---
        with subaba2:
            st.subheader("💰 Controle Financeiro")
            
            from database import (
                buscar_valor_futebol, salvar_valor_futebol
            )
            
            # CAIXA GERAL
            st.markdown("**🏦 CAIXA GERAL (Acumulado)**")
            saldo_geral = calcular_saldo_total()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💵 Receitas", f"R$ {saldo_geral['entrada']:.2f}")
            
            with col2:
                st.metric("💸 Despesas", f"R$ {saldo_geral['despesa']:.2f}")
            
            with col3:
                if saldo_geral['saldo'] >= 0:
                    st.success(f"💰 SALDO: R$ {saldo_geral['saldo']:.2f}")
                else:
                    st.error(f"💰 SALDO: R$ {saldo_geral['saldo']:.2f}")
            
            st.divider()
            
            # CONFIGURAÇÃO
            st.subheader("⚙️ Configuração")
            valor_atual = buscar_valor_futebol()
            valor_futebol = st.number_input("Valor do futebol (R$):", min_value=0.0, value=valor_atual, key="config_valor")
            
            if st.button("💾 Salvar Valor"):
                salvar_valor_futebol(valor_futebol)
                st.success(f"✅ Valor definido: R$ {valor_futebol:.2f}")
            
            st.divider()
            
            # RESUMO POR DATA
            st.subheader("📅 Resumo por Data")
            
            data_sorteio_fin = buscar_data_jogo_atual()
            
            if data_sorteio_fin:
                saldo_data = calcular_saldo_por_data(str(data_sorteio_fin))
                total_pag = total_pagamentos(str(data_sorteio_fin))
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(f"📥 Entrada ({data_sorteio_fin})", f"R$ {saldo_data['entrada']:.2f}")
                
                with col2:
                    st.metric(f"👥 Pagantes", f"{total_pag} jogadores")
                
                with col3:
                    st.metric(f"📤 Despesa ({data_sorteio_fin})", f"R$ {saldo_data['despesa']:.2f}")
                
                st.divider()
                
                # REGISTRAR DESPESA
                st.subheader("➕ Registrar Despesa")
                despesa_desc = st.text_input("Descrição:", key="desc_desp")
                despesa_valor = st.number_input("Valor (R$):", min_value=0.0, key="val_desp")
                
                if st.button("➕ Adicionar"):
                    if despesa_desc and despesa_valor > 0:
                        inserir_despesa(str(data_sorteio_fin), despesa_desc, despesa_valor, st.session_state.admin_id)
                        st.success(f"✅ Despesa adicionada!")
                
                st.divider()
                
                # QUEM PAGOU
                st.subheader("👥 Quem Pagou")
                pagamentos = contar_pagamentos(str(data_sorteio_fin))
                
                if pagamentos:
                    for idx, (nome, jog_id) in enumerate(pagamentos):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(f"✅ {nome}")
                        with col2:
                            if st.button("❌", key=f"del_pag_fin_{idx}_{jog_id}"):
                                desmarcar_pagamento(jog_id, str(data_sorteio_fin))
                                st.success("Removido!")
                                st.rerun()
                else:
                    st.info("Ninguém pagou ainda")
                
                st.divider()
                
                # DESPESAS
                st.subheader("🗑️ Despesas Registradas")
                despesas = buscar_despesas(str(data_sorteio_fin))
                
                if despesas:
                    for desc, valor, admin_id in despesas:
                        st.write(f"📌 **{desc}**: R$ {valor:.2f}")
                else:
                    st.info("Nenhuma despesa registrada")