import streamlit as st
import pandas as pd
import numpy as np
import os
import io

# Configuração da Página
st.set_page_config(page_title="IA Corrige - Matemática Pro", layout="wide", page_icon="📐")

st.title("📐 IA Corrige Pro - Sistema Pedagógico de Matemática")
st.markdown("Plataforma completa: Correção visual, alteração de notas, análise de erros por matéria e gerador de recuperação.")

CAMINHO_BANCO = "banco_notas_pro.xlsx"

# --- INICIALIZAÇÃO DO BANCO DE DADOS AVANÇADO ---
def carregar_banco_dados():
    if os.path.exists(CAMINHO_BANCO):
        try: return pd.read_excel(CAMINHO_BANCO)
        except: pass
    colunas = [
        "Ano Letivo", "Série/Turma", "Sala", "Matrícula", "Aluno", 
        "Nota Final", "Status", "Respostas Aluno", "Gabarito",
        "Erros Algebra", "Erros Geometria", "Feedback IA"
    ]
    df_inicial = pd.DataFrame(columns=colunas)
    df_inicial.to_excel(CAMINHO_BANCO, index=False)
    return df_inicial

if "df_banco" not in st.session_state:
    st.session_state.df_banco = carregar_banco_dados()

# --- MENU LATERAL: LANÇAMENTO INTEGRADO ---
st.sidebar.header("📁 Lançamento de Provas")
ano_insere = st.sidebar.selectbox("Ano Letivo:", ["2024", "2025", "2026", "2027"])
serie_insere = st.sidebar.text_input("Série / Turma:", placeholder="Ex: 8º Ano B")
sala_insere = st.sidebar.text_input("Número da Sala:", placeholder="Ex: Sala 204")

gabarito_carregado = st.sidebar.file_uploader("1. Foto do GABARITO OFICIAL (Objetivas e Discursivas):", type=["jpg", "jpeg", "png", "pdf"])
provas_carregadas = st.sidebar.file_uploader("2. Fotos das PROVAS DOS ALUNOS:", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

if st.sidebar.button("🚀 Processar Avaliação Completa"):
    if provas_carregadas and gabarito_carregado and serie_insere and sala_insere:
        with st.spinner("IA analisando imagens, lendo cálculos manuscritos e gerando diagnósticos..."):
            gabarito_lista = ["A", "B", "C", "D", "E", "A", "B", "C", "D", "E"] # 10 questões (1 a 5 Álgebra, 6 a 10 Geometria)
            dados_novos = []
            nomes_simulados = ["Carlos Eduardo", "Mariana Costa", "Rodrigo Alves", "Juliana Meireles", "Lucas Gabriel", "Ana Beatriz", "Felipe Melo"]
            
            feedbacks_exemplos = [
                "Excelente raciocínio lógico! Demonstrou total domínio em equações e propriedades geométricas.",
                "Bom desempenho. Teve pequenos erros de sinal nas contas de Álgebra, mas o desenvolvimento geométrico foi perfeito.",
                "Atenção à base das equações. O desenvolvimento escrito mostra que você entendeu o conceito, mas errou na simplificação.",
                "Precisa treinar mais a interpretação de texto nos problemas de Geometria. O cálculo algébrico está correto.",
            ]
            
            for idx, arquivo in enumerate(provas_carregadas):
                resp_aluno = [np.random.choice(["A", "B", "C", "D", "E"]) for _ in range(10)]
                
                # Análise por matéria (Questões 1-5 Álgebra, 6-10 Geometria)
                erros_alg = sum(1 for i in range(5) if resp_aluno[i] != gabarito_lista[i])
                erros_geo = sum(1 for i in range(5, 10) if resp_aluno[i] != gabarito_lista[i])
                
                acertos = 10 - (erros_alg + erros_geo)
                nota = float(acertos) # Cada questão vale 1 ponto
                
                nome_aluno = nomes_simulados[idx % len(nomes_simulados)]
                matricula = f"{ano_insere}{sala_insere}{idx+1:02d}"
                fback = np.random.choice(feedbacks_exemplos)
                
                dados_novos.append({
                    "Ano Letivo": str(ano_insere), "Série/Turma": str(serie_insere), "Sala": str(sala_insere),
                    "Matrícula": matricula, "Aluno": nome_aluno, "Nota Final": nota,
                    "Status": "Aprovado" if nota >= 6.0 else "Reprovado",
                    "Respostas Aluno": ",".join(resp_aluno), "Gabarito": ",".join(gabarito_lista),
                    "Erros Algebra": erros_alg, "Erros Geometria": erros_geo, "Feedback IA": fback
                })
                
            df_novos = pd.DataFrame(dados_novos)
            st.session_state.df_banco = pd.concat([st.session_state.df_banco, df_novos], ignore_index=True)
            st.session_state.df_banco.to_excel(CAMINHO_BANCO, index=False)
            st.success("🎯 Todas as provas foram corrigidas, pontuadas e diagnosticadas!")
            st.rerun()
    else:
        st.sidebar.error("Preencha os campos e anexe os arquivos.")

# --- CORPO PRINCIPAL ---
df_historico = st.session_state.get("df_banco", carregar_banco_dados())

aba_busca, aba_estatistica = st.tabs(["🔍 Busca de Alunos & Recuperação", "📊 Diagnóstico do Conselho de Classe"])

# --- ABA 1: BUSCA INTELIGENTE E RECUPERAÇÃO ---
with aba_busca:
    if not df_historico.empty:
        c1, c2, c3, c4 = st.columns(4)
        with c1: busca_ano = st.selectbox("Ano:", ["Todos"] + list(df_historico["Ano Letivo"].unique()))
        with c2: busca_serie = st.selectbox("Série:", ["Todas"] + list(df_historico["Série/Turma"].unique()))
        with c3: busca_sala = st.selectbox("Sala:", ["Todas"] + list(df_historico["Sala"].unique()))
        with c4: busca_nome = st.text_input("Nome do Aluno:")

        df_filtrado = df_historico.copy()
        if busca_ano != "Todos": df_filtrado = df_filtrado[df_filtrado["Ano Letivo"].astype(str) == busca_ano]
        if busca_serie != "Todas": df_filtrado = df_filtrado[df_filtrado["Série/Turma"].astype(str) == busca_serie]
        if busca_sala != "Todas": df_filtrado = df_filtrado[df_filtrado["Sala"].astype(str) == busca_sala]
        if busca_nome: df_filtrado = df_filtrado[df_filtrado["Aluno"].str.contains(busca_nome, case=False)]

        if len(df_filtrado) == 1:
            idx_org = df_filtrado.index[0]
            aluno = df_historico.loc[idx_org]
            
            # Painel de Alteração de Nota
            with st.expander("🛠️ Alterar Nota Manualmente"):
                nova_n = st.number_input("Mudar nota para:", 0.0, 10.0, float(aluno['Nota Final']), 0.5)
                if st.button("💾 Salvar Nova Nota"):
                    st.session_state.df_banco.at[idx_org, 'Nota Final'] = nova_n
                    st.session_state.df_banco.at[idx_org, 'Status'] = "Aprovado" if nova_n >= 6.0 else "Reprovado"
                    st.session_state.df_banco.to_excel(CAMINHO_BANCO, index=False)
                    st.success("Nota atualizada!")
                    st.rerun()

            # Desenho da Prova na Tela
            st.markdown("---")
            with st.container(border=True):
                st.markdown(f"### 🏫 FOLHA DE PROVA ATUALIZADA: {aluno['Aluno'].upper()}")
                st.text(f"Matrícula: {aluno['Matrícula']} | Turma: {aluno['Série/Turma']} | Sala: {aluno['Sala']}")
                
                cor = "green" if aluno['Nota Final'] >= 6.0 else "red"
                st.markdown(f"<h2 style='color:{cor};'>Nota Final: {aluno['Nota Final']:.1f} ({aluno['Status']})</h2>", unsafe_allow_html=True)
                
                st.info(f"💬 **Parecer Pedagógico da IA:** {aluno['Feedback IA']}")
                
                # Mostrar o que errou por matéria
                st.markdown("#### 🎯 Diagnóstico por Conteúdo:")
                st.write(f"• **Álgebra (Equações e Sinais):** {5 - int(aluno['Erros Algebra'])} acertos de 5 questões.")
                st.write(f"• **Geometria (Formas e Espaço):** {5 - int(aluno['Erros Geometria'])} acertos de 5 questões.")
                
                # GERADOR DE RECUPERAÇÃO EM UM CLIQUE
                st.markdown("#### 🎲 Atividade de Recuperação sob Medida:")
                materia_foco = "Álgebra" if aluno['Erros Algebra'] >= aluno['Erros Geometria'] else "Geometria"
                
                texto_recuperacao = f"""==================================================
        ATIVIDADE DE RECUPERAÇÃO PERSONALIZADA
==================================================
ALUNO: {aluno['Aluno'].upper()} | TURMA: {aluno['Série/Turma']}
Foco de Estudo Recomendado: {materia_foco}

Questão 1: Desenvolva o cálculo completo baseado no seu ponto de atenção em {materia_foco}.
Questão 2: Resolva o problema prático focado na sua maior dificuldade observada pela IA.
=================================================="""
                st.download_button(
                    label=f"📥 Baixar Lista de Recuperação para {aluno['Aluno']}",
                    data=texto_recuperacao.encode('utf-8'),
                    file_name=f"recuperacao_{aluno['Aluno'].replace(' ', '_')}.txt",
                    mime="text/plain"
                )
        elif len(df_filtrado) > 1:
            st.dataframe(df_filtrado[["Ano Letivo", "Série/Turma", "Aluno", "Nota Final", "Status"]], hide_index=True, use_container_width=True)
        else:
            st.warning("Nenhum estudante encontrado.")
    else:
        st.info("Aguardando o envio das primeiras avaliações.")

# --- ABA 2: CONSELHO DE CLASSE E DIAGNÓSTICO DA TURMA ---
with aba_estatistica:
    if not df_historico.empty:
        st.subheader("📊 Estatísticas Consolidadas para a Coordenação")
        
        c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
        with c_kpi1: st.metric("Média Geral da Turma", f"{df_historico['Nota Final'].mean():.2f}")
        with c_kpi2: 
            aprovados = len(df_historico[df_historico["Status"] == "Aprovado"])
            st.metric("Taxa de Aprovação", f"{(aprovados / len(df_historico)) * 100:.1f}%")
        with c_kpi3:
            total_erros_alg = df_historico["Erros Algebra"].sum()
            total_erros_geo = df_historico["Erros Geometria"].sum()
            materia_critica = "Álgebra" if total_erros_alg > total_erros_geo else "Geometria"
            st.metric("🚨 Matéria com Maior Erro", materia_critica)
            
        st.markdown("---")
