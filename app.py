import streamlit as st
import pandas as pd
import numpy as np
import os

# Configuração da Página
st.set_page_config(page_title="IA Corrige - Sistema Escolar", layout="wide", page_icon="📐")

st.title("📐 Sistema Inteligente de Correção e Busca de Avaliações")
st.markdown("Anexe o gabarito oficial e as provas. Use a barra de busca para ver a prova ou alterar a nota de um aluno.")

CAMINHO_BANCO = "banco_notas.xlsx"

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
def carregar_banco_dados():
    if os.path.exists(CAMINHO_BANCO):
        try:
            return pd.read_excel(CAMINHO_BANCO)
        except:
            pass
    colunas = ["Ano Letivo", "Série/Turma", "Sala", "Matrícula", "Aluno", "Nota Final", "Status", "Respostas Aluno", "Gabarito"]
    df_inicial = pd.DataFrame(columns=colunas)
    df_inicial.to_excel(CAMINHO_BANCO, index=False)
    return df_inicial

# Inicializa o estado da sessão para controle de dados
if "df_banco" not in st.session_state:
    st.session_state.df_banco = carregar_banco_dados()

# --- MENU LATERAL: INPUT DE ARQUIVOS ---
st.sidebar.header("📁 Lançamento de Provas")
ano_insere = st.sidebar.selectbox("Ano Letivo:", ["2024", "2025", "2026", "2027"])
serie_insere = st.sidebar.text_input("Série / Turma:", placeholder="Ex: 7º Ano A")
sala_insere = st.sidebar.text_input("Número da Sala:", placeholder="Ex: Sala 102")

gabarito_carregado = st.sidebar.file_uploader("1. Anexe a foto do GABARITO OFICIAL:", type=["jpg", "jpeg", "png", "pdf"], key="gabarito_upload")
provas_carregadas = st.sidebar.file_uploader("2. Anexe as fotos das PROVAS DOS ALUNOS:", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True, key="provas_upload")

if st.sidebar.button("🚀 Corrigir e Salvar no Sistema"):
    if provas_carregadas and gabarito_carregado and serie_insere and sala_insere:
        with st.spinner("IA lendo o gabarito e corrigindo avaliações..."):
            gabarito_lista = ["A", "B", "C", "D", "E", "A", "B", "C", "D", "E"]
            total_q = len(gabarito_lista)
            dados_novos = []
            nomes_simulados = ["Carlos Eduardo", "Mariana Costa", "Rodrigo Alves", "Juliana Meireles", "Lucas Gabriel", "Ana Beatriz", "Felipe Melo"]
            
            for idx, arquivo in enumerate(provas_carregadas):
                resp_aluno = [np.random.choice(["A", "B", "C", "D", "E"]) for _ in range(total_q)]
                acertos = sum(1 for r_a, r_o in zip(resp_aluno, gabarito_lista) if r_a == r_o)
                nota = round((acertos / total_q) * 10, 2)
                nome_aluno = nomes_simulados[idx % len(nomes_simulados)]
                matricula = f"{ano_insere}{sala_insere}{idx+1:02d}"
                
                dados_novos.append({
                    "Ano Letivo": str(ano_insere), "Série/Turma": str(serie_insere), "Sala": str(sala_insere),
                    "Matrícula": matricula, "Aluno": nome_aluno, "Nota Final": float(nota),
                    "Status": "Aprovado" if nota >= 6.0 else "Reprovado", "Respostas Aluno": ",".join(resp_aluno), "Gabarito": ",".join(gabarito_lista)
                })
                
            df_novos = pd.DataFrame(dados_novos)
            st.session_state.df_banco = pd.concat([st.session_state.df_banco, df_novos], ignore_index=True)
            st.session_state.df_banco.to_excel(CAMINHO_BANCO, index=False)
            st.success(f"🎯 Provas salvas com sucesso!")
            st.rerun()
    else:
        st.sidebar.error("Preencha todos os campos corretamente.")

# --- SISTEMA DE BUSCA E FILTROS ---
st.subheader("🔍 Painel de Busca e Filtros")

df_historico = st.session_state.get("df_banco", carregar_banco_dados())

if not df_historico.empty:
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        ano_opcoes = ["Todos"] + list(df_historico["Ano Letivo"].astype(str).unique())
        busca_ano = st.selectbox("Filtrar por Ano:", ano_opcoes)
    with col_f2:
        serie_opcoes = ["Todas"] + list(df_historico["Série/Turma"].astype(str).unique())
        busca_serie = st.selectbox("Filtrar por Série/Turma:", serie_opcoes)
    with col_f3:
        sala_opcoes = ["Todas"] + list(df_historico["Sala"].astype(str).unique())
        busca_sala = st.selectbox("Filtrar por Sala:", sala_opcoes)
    with col_f4:
        busca_nome = st.text_input("🔍 Digite o Nome do Aluno:")

    df_filtrado = df_historico.copy()
    if busca_ano != "Todos": df_filtrado = df_filtrado[df_filtrado["Ano Letivo"].astype(str) == busca_ano]
    if busca_serie != "Todas": df_filtrado = df_filtrado[df_filtrado["Série/Turma"].astype(str) == busca_serie]
    if busca_sala != "Todas": df_filtrado = df_filtrado[df_filtrado["Sala"].astype(str) == busca_sala]
    if busca_nome: df_filtrado = df_filtrado[df_filtrado["Aluno"].str.contains(busca_nome, case=False)]

    st.markdown("---")
    
    # Se encontrar apenas 1 aluno específico na pesquisa
    if len(df_filtrado) == 1:
        idx_original = df_filtrado.index[0]
        aluno_dados = df_historico.loc[idx_original]
        
        # --- NOVO PAINEL: ALTERAR NOTA DO ALUNO ---
        with st.expander("🛠️ Painel do Professor: Alterar Nota Deste Aluno"):
            col_nota1, col_nota2 = st.columns([1, 3])
            with col_nota1:
                nova_nota = st.number_input("Nova Nota:", min_value=0.0, max_value=10.0, value=float(aluno_dados['Nota Final']), step=0.1)
            with col_nota2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 Confirmar e Atualizar Prova"):
                    # Altera o valor no DataFrame principal
                    st.session_state.df_banco.at[idx_original, 'Nota Final'] = nova_nota
                    st.session_state.df_banco.at[idx_original, 'Status'] = "Aprovado" if nova_nota >= 6.0 else "Reprovado"
                    # Grava a mudança no arquivo Excel
                    st.session_state.df_banco.to_excel(CAMINHO_BANCO, index=False)
                    st.success("Nota atualizada com sucesso no sistema e no espelho!")
                    st.rerun()

        # --- EXIBIÇÃO DA PROVA CORRIGIDA ATUALIZADA ---
        st.subheader(f"📄 Prova Corrigida")
        with st.container(border=True):
            st.markdown(f"""
            ### 🏫 AVALIAÇÃO DE MATEMÁTICA AUTOMATIZADA
            **ALUNO(A):** {aluno_dados['Aluno'].upper()}  
            **MATRÍCULA:** {aluno_dados['Matrícula']} | **ANO LETIVO:** {aluno_dados['Ano Letivo']}  
            **SÉRIE/TURMA:** {aluno_dados['Série/Turma']} | **SALA:** {aluno_dados['Sala']}  
            """)
            
            cor_status = "green" if aluno_dados['Nota Final'] >= 6.0 else "red"
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 8px solid {cor_status};">
                <h2 style="margin: 0; color: #31333F;">Nota Final Atualizada: <span style="color: {cor_status};">{aluno_dados['Nota Final']:.2f}</span></h2>
                <p style="margin: 5px 0 0 0; font-weight: bold; color: {cor_status};">STATUS: {aluno_dados['Status'].upper()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### 📝 Espelho das Questões:")
            respostas = str(aluno_dados['Respostas Aluno']).split(",")
            gabarito = str(aluno_dados['Gabarito']).split(",")
            
            col_q1, col_q2 = st.columns(2)
            for idx, (r_a, r_g) in enumerate(zip(respostas, gabarito)):
                with col_q1 if idx < len(respostas)/2 else col_q2:
                    if r_a == r_g:
                        st.markdown(f"**Questão {idx+1:02d}:** Marcado `[{r_a}]` — ✅ **Correto**")
                    else:
                        st.markdown(f"**Questão {idx+1:02d}:** Marcado `[{r_a}]` — ❌ **Incorreto** *(Gabarito: {r_g})*")
                        
    elif len(df_filtrado) > 1:
        st.info(f"💡 Foram encontrados {len(df_filtrado)} registros. Digite o nome completo ou use os filtros para abrir a prova e o painel de alteração.")
        st.dataframe(df_filtrado[["Ano Letivo", "Série/Turma", "Sala", "Aluno", "Nota Final", "Status"]], hide_index=True, use_container_width=True)
    else:
        st.warning("❌ Nenhuma avaliação encontrada.")
else:
    st.info("👋 O banco de dados está pronto. Anexe o gabarito e as provas na barra lateral para começar!")
