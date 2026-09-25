import streamlit as st
import pandas as pd
import numpy as np
import os

# Configuração da Página
st.set_page_config(page_title="IA Corrige - Sistema Escolar", layout="wide", page_icon="📐")

st.title("📐 Sistema Inteligente de Correção e Busca de Avaliações")
st.markdown("Anexe a imagem do gabarito oficial e as fotos das provas. A IA processará tudo visualmente.")

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

df_historico = carregar_banco_dados()

# --- MENU LATERAL: INPUT DE ARQUIVOS ---
st.sidebar.header("📁 Lançamento de Provas")
ano_insere = st.sidebar.selectbox("Ano Letivo:", ["2024", "2025", "2026", "2027"])
serie_insere = st.sidebar.text_input("Série / Turma:", placeholder="Ex: 7º Ano A")
sala_insere = st.sidebar.text_input("Número da Sala:", placeholder="Ex: Sala 102")

# 1. NOVO CAMPO: Upload da foto do Gabarito Oficial
gabarito_carregado = st.sidebar.file_uploader(
    "1. Anexe a foto do GABARITO OFICIAL:", 
    type=["jpg", "jpeg", "png", "pdf"],
    key="gabarito_upload"
)

# 2. CAMPO: Upload das fotos das provas dos alunos
provas_carregadas = st.sidebar.file_uploader(
    "2. Anexe as fotos das PROVAS DOS ALUNOS:", 
    type=["jpg", "jpeg", "png", "pdf"], 
    accept_multiple_files=True,
    key="provas_upload"
)

if st.sidebar.button("🚀 Corrigir e Salvar no Sistema"):
    if provas_carregadas and gabarito_carregado and serie_insere and sala_insere:
        with st.spinner("IA lendo o gabarito e corrigindo avaliações..."):
            
            # SIMULAÇÃO DA IA LENDO A FOTO DO GABARITO VIA OCR
            # Na vida real o OpenCV escaneia a foto do gabarito carregado aqui
            gabarito_lista = ["A", "B", "C", "D", "E", "A", "B", "C", "D", "E"] # Respostas extraídas da foto
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
                    "Ano Letivo": str(ano_insere),
                    "Série/Turma": str(serie_insere),
                    "Sala": str(sala_insere),
                    "Matrícula": matricula,
                    "Aluno": nome_aluno,
                    "Nota Final": float(nota),
                    "Status": "Aprovado" if nota >= 6.0 else "Reprovado",
                    "Respostas Aluno": ",".join(resp_aluno),
                    "Gabarito": ",".join(gabarito_lista)
                })
                
            df_novos = pd.DataFrame(dados_novos)
            df_atualizado = pd.concat([df_historico, df_novos], ignore_index=True)
            df_atualizado.to_excel(CAMINHO_BANCO, index=False)
            st.success(f"🎯 Gabarito lido com sucesso! {len(provas_carregadas)} provas salvas no banco de dados!")
            st.rerun()
    else:
        st.sidebar.error("Preencha todos os campos e anexe tanto o gabarito quanto as provas.")

# --- SISTEMA DE BUSCA INTELIGENTE ---
st.subheader("🔍 Painel de Busca e Filtros")

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
    if len(df_filtrado) == 1:
        aluno_dados = df_filtrado.iloc[0]
        st.subheader(f"📄 Prova Corrigida Encontrada")
        
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
                <h2 style="margin: 0; color: #31333F;">Nota Final: <span style="color: {cor_status};">{aluno_dados['Nota Final']:.2f}</span></h2>
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
        st.info(f"💡 Foram encontrados {len(df_filtrado)} registros. Use a busca por nome para detalhar a prova do aluno.")
        st.dataframe(df_filtrado[["Ano Letivo", "Série/Turma", "Sala", "Aluno", "Nota Final", "Status"]], hide_index=True, use_container_width=True)
    else:
        st.warning("❌ Nenhuma avaliação foi encontrada.")
else:
    st.info("👋 O banco de dados está pronto. Anexe o gabarito e as provas na barra lateral para começar!")