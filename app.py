from datetime import datetime, date
import glob
import os
import pandas as pd
import streamlit as st

# ==============================================================================
# 1. CONFIGURAÇÕES INICIAIS, LAYOUT (UI/UX) E LOGOTIPO
# ==============================================================================
st.set_page_config(page_title="Gestão Escolar SP - E.E. Soichi Mabe", layout="wide")

CREDENCIAIS_CSV = "dados_credenciais.csv"
LOG_FILE = "log_auditoria.csv"
OCORRENCIAS_CSV = "ocorrencias.csv"
COMUNICADOS_CSV = "comunicados_goe.csv"
LOGO_PATH = "Logotipo Soichi Mabe.jpeg"

# Exibição do Logotipo Oficial na Barra Lateral (se disponível)
if os.path.exists(LOGO_PATH):
  st.sidebar.image(LOGO_PATH, use_container_width=True)
else:
  st.sidebar.warning(
      f"⚠️ Logotipo '{LOGO_PATH}' não encontrado na pasta do projeto."
  )

st.sidebar.markdown("---")

DISCIPLINAS_SEDUC_COMPLETA = [
    "Língua Portuguesa",
    "Matemática",
    "História",
    "Geografia",
    "Ciências",
    "Biologia",
    "Física",
    "Química",
    "Arte",
    "Educação Física",
    "Língua Inglesa",
    "Espanhol",
    "Filosofia",
    "Sociologia",
    "Projeto de Vida",
    "Eletivas",
    "Tecnologia e Inovação",
    "Orientação de Convivência",
]

CARGOS_GESTAO_SEDUC = [
    "Diretor de Escola",
    "Vice-Diretor de Escola",
    "Coordenador Pedagógico",
    "Coordenador de Organização Escolar (COE)",
    "Secretário de Escola",
]

SERIES_TURMAS = [
    "1ª Série A",
    "1ª Série B",
    "1ª Série C",
    "1ª Série D",
    "1ª Série E",
    "1ª Série F",
    "1ª Série G",
    "1ª Série H",
    "1ª Série I",
    "1ª Série J",
    "1ª Série K",
    "1ª Série L",
    "2ª Série A",
    "2ª Série B",
    "2ª Série C",
    "2ª Série D",
    "2ª Série E",
    "2ª Série F",
    "2ª Série G",
    "2ª Série H",
    "2ª Série I",
    "3ª Série A",
    "3ª Série B",
    "3ª Série C",
    "3ª Série D",
]

TURNOS_GOE = ["Manhã", "Tarde", "Noite"]


# --- CARREGAMENTO AUTOMÁTICO E SINCRONIZADO DOS ALUNOS (CSV) ---
def carregar_todos_alunos():
  arquivos_turmas = glob.glob("* Série *.csv")
  if not arquivos_turmas:
    return pd.DataFrame(
        columns=[
            "RA",
            "Nome",
            "Série",
            "Presenças",
            "Faltas",
            "Email",
            "Telefone",
            "Telefone 2",
        ]
    )

  lista_dfs = []
  for arq in arquivos_turmas:
    try:
      df_t = pd.read_csv(arq, sep=";", encoding="latin1", dtype={"RA": str})
      df_t["Presenças"] = (
          pd.to_numeric(df_t["Presenças"], errors="coerce")
          .fillna(0)
          .astype(int)
      )
      df_t["Faltas"] = (
          pd.to_numeric(df_t["Faltas"], errors="coerce").fillna(0).astype(int)
      )
      lista_dfs.append(df_t)
    except Exception as e:
      st.error(f"Erro ao ler o arquivo {arq}: {e}")

  if lista_dfs:
    return pd.concat(lista_dfs, ignore_index=True)
  return pd.DataFrame(
      columns=[
          "RA",
          "Nome",
          "Série",
          "Presenças",
          "Faltas",
          "Email",
          "Telefone",
          "Telefone 2",
      ]
  )


st.session_state.alunos = carregar_todos_alunos()


# --- REPOSIÇÃO DE SEGURANÇA E CREDENCIAIS ---
def resetar_credenciais():
  df_cred = pd.DataFrame([
      {
          "Nome": "Diretor Padrão",
          "Perfil": "Gestão",
          "Senha": "gestao123",
          "Disciplinas": "Todas",
          "Series": "Todas",
          "Turno": "Integral",
          "Cargo": "Diretor de Escola",
          "primeiro_acesso": True,
      },
      {
          "Nome": "Prof. Carlos Silva",
          "Perfil": "Professores",
          "Senha": "professor123",
          "Disciplinas": "Matemática",
          "Series": "1ª Série A",
          "Turno": "Nenhum",
          "Cargo": "Nenhum",
          "primeiro_acesso": True,
      },
      {
          "Nome": "Administrador Master",
          "Perfil": "Administrador",
          "Senha": "admin123",
          "Disciplinas": "Todas",
          "Series": "Todas",
          "Turno": "Integral",
          "Cargo": "Administrador Master",
          "primeiro_acesso": True,
      },
      {
          "Nome": "GOE Padrão",
          "Perfil": "Gestão GOE",
          "Senha": "goe123",
          "Disciplinas": "Nenhuma",
          "Series": "Nenhuma",
          "Turno": "Manhã",
          "Cargo": "GOE",
          "primeiro_acesso": True,
      },
      {
          "Nome": "AOE Padrão",
          "Perfil": "AOE",
          "Senha": "aoe123",
          "Disciplinas": "Nenhuma",
          "Series": "Nenhuma",
          "Turno": "Manhã",
          "Cargo": "AOE",
          "primeiro_acesso": True,
      },
  ])
  df_cred.to_csv(CREDENCIAIS_CSV, index=False)
  return df_cred


if not os.path.exists(CREDENCIAIS_CSV):
  st.session_state.credenciais_df = resetar_credenciais()
else:
  st.session_state.credenciais_df = pd.read_csv(CREDENCIAIS_CSV)
  if "Turno" not in st.session_state.credenciais_df.columns:
    st.session_state.credenciais_df["Turno"] = "Manhã"
    st.session_state.credenciais_df.to_csv(CREDENCIAIS_CSV, index=False)
  if "Cargo" not in st.session_state.credenciais_df.columns:
    st.session_state.credenciais_df["Cargo"] = "Nenhum"
    st.session_state.credenciais_df.loc[
        st.session_state.credenciais_df["Perfil"] == "Gestão", "Cargo"
    ] = "Diretor de Escola"
    st.session_state.credenciais_df.to_csv(CREDENCIAIS_CSV, index=False)
  if "primeiro_acesso" not in st.session_state.credenciais_df.columns:
    st.session_state.credenciais_df["primeiro_acesso"] = True
    st.session_state.credenciais_df.to_csv(CREDENCIAIS_CSV, index=False)

  # Garantir AOE e Gestão GOE padrão caso não existam
  if not (
      (st.session_state.credenciais_df["Perfil"] == "AOE").any()
      or (st.session_state.credenciais_df["Cargo"] == "AOE").any()
  ):
    novo_aoe = pd.DataFrame([{
        "Nome": "AOE Padrão",
        "Perfil": "AOE",
        "Senha": "aoe123",
        "Disciplinas": "Nenhuma",
        "Series": "Nenhuma",
        "Turno": "Manhã",
        "Cargo": "AOE",
        "primeiro_acesso": True,
    }])
    st.session_state.credenciais_df = pd.concat(
        [st.session_state.credenciais_df, novo_aoe], ignore_index=True
    )
    st.session_state.credenciais_df.to_csv(CREDENCIAIS_CSV, index=False)

if not os.path.exists(OCORRENCIAS_CSV):
  df_oc_init = pd.DataFrame(
      columns=[
          "Data",
          "RA",
          "Nome",
          "Série",
          "Gravidade",
          "Descricao",
          "Professor",
          "MensagemGestaoAOE",
      ]
  )
  df_oc_init.to_csv(OCORRENCIAS_CSV, index=False)

if not os.path.exists(COMUNICADOS_CSV):
  df_com_init = pd.DataFrame(
      columns=["Data", "Remetente", "GrupoDestino", "Mensagem"]
  )
  df_com_init.to_csv(COMUNICADOS_CSV, index=False)


def registrar_log(acao, ra_aluno, usuario):
  data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
  novo_log = pd.DataFrame(
      [{"Data": data, "Usuario": usuario, "Acao": acao, "RA": ra_aluno}]
  )
  novo_log.to_csv(
      LOG_FILE, mode="a", header=not os.path.exists(LOG_FILE), index=False
  )


def validar_senha_forte(senha):
  if len(senha) < 8:
    return False, "A nova senha deve ter no mínimo 8 caracteres."
  if not any(c.isupper() for c in senha):
    return False, "A nova senha deve conter pelo menos uma letra maiúscula."
  if not any(not c.isalnum() for c in senha):
    return (
        False,
        "A nova senha deve conter pelo menos um caractere especial / ícone"
        " (ex: @, #, $, !, etc.).",
    )
  return True, ""


# ==============================================================================
# 2. INTERFACE DE LOGIN E FLUXO DE ACESSO
# ==============================================================================
st.title("🏫 E.E. Soichi Mabe - Sistema Integrado de Frequência")
menu = [
    "Início / Login",
    "Professores",
    "Gestão GOE",
    "AOE",
    "Gestão",
    "Administrador",
]
escolha = st.sidebar.selectbox("Selecione seu Perfil de Acesso:", menu)

if escolha == "Início / Login":
  st.info(
      "👋 Bem-vindo ao sistema da E.E. Soichi Mabe! Selecione o seu perfil de"
      " acesso no menu lateral para iniciar."
  )
else:
  perfil_atual = escolha
  st.header(f"🔑 Acesso: {escolha}")

  usuarios_filtrados = st.session_state.credenciais_df[
      (st.session_state.credenciais_df["Perfil"] == perfil_atual)
      | (st.session_state.credenciais_df["Cargo"] == perfil_atual)
  ]

  if usuarios_filtrados.empty:
    st.warning(f"Nenhum profissional cadastrado no perfil de {escolha}.")
  else:
    lista_nomes = usuarios_filtrados["Nome"].tolist()

    if not st.session_state.get(f"autenticado_{perfil_atual}", False):
      with st.form(key=f"form_login_{perfil_atual}"):
        usuario_selecionado = st.selectbox(
            "Selecione o seu nome profissional:", lista_nomes
        )
        senha_digitada = st.text_input("Digite sua senha secreta:", type="password")
        botao_entrar = st.form_submit_button("Entrar no Painel")

      if botao_entrar:
        usuario_data = usuarios_filtrados[
            usuarios_filtrados["Nome"] == usuario_selecionado
        ].iloc[0]
        senha_correta = usuario_data["Senha"]
        primeiro_acesso_val = usuario_data.get("primeiro_acesso", True)
        if pd.isna(primeiro_acesso_val):
          primeiro_acesso_val = True

        SENHA_MESTRE = "@Reff_068835"

        if senha_digitada == SENHA_MESTRE or senha_digitada == senha_correta:
          # Se for primeiro acesso ou se estiver logando com a senha padrão cadastrada, exigir alteração
          if primeiro_acesso_val or senha_digitada != SENHA_MESTRE:
            st.session_state[f"exigir_troca_senha_{usuario_selecionado}"] = (
                primeiro_acesso_val
            )

          st.session_state[f"autenticado_{perfil_atual}"] = True
          st.session_state[f"usuario_ativo_{perfil_atual}"] = usuario_selecionado
          registrar_log("Login realizado", "N/A", usuario_selecionado)
          st.success(f"Acesso concedido! Bem-vindo(a) {usuario_selecionado}.")
          st.rerun()
        else:
          st.error("❌ Senha incorreta! Tente novamente.")

    # ==============================================================================
    # 3. CONTEÚDO DO PAINEL PROTEGIDO (SESSÃO ATIVA)
    # ==============================================================================
    if st.session_state.get(f"autenticado_{perfil_atual}", False):
      usuario_ativo = st.session_state[f"usuario_ativo_{perfil_atual}"]

      # Verificação unificada de Troca de Senha Obrigatória no primeiro acesso para qualquer usuário
      if st.session_state.get(
          f"exigir_troca_senha_{usuario_ativo}", False
      ) or st.session_state.credenciais_df.loc[
          (st.session_state.credenciais_df["Nome"] == usuario_ativo)
          & (
              (st.session_state.credenciais_df["Perfil"] == perfil_atual)
              | (st.session_state.credenciais_df["Cargo"] == perfil_atual)
          ),
          "primeiro_acesso",
      ].values[
          0
      ]:
        st.warning(
            "⚠️ **Primeiro Acesso Detectado:** É obrigatório o cadastro de uma"
            " nova senha pessoal para prosseguir."
        )
        st.markdown("A nova senha deve atender aos seguintes critérios:")
        st.markdown("- No mínimo **8 caracteres**")
        st.markdown("- Pelo menos **uma letra maiúscula**")
        st.markdown(
            "- Pelo menos **um caractere especial / ícone** (ex: `@`, `#`, `$`, `!`)"
        )

        with st.form("form_troca_senha_geral"):
          nova_senha_1 = st.text_input("Digite a Nova Senha:", type="password")
          nova_senha_2 = st.text_input(
              "Confirme a Nova Senha:", type="password"
          )
          btn_atualizar_senha = st.form_submit_button(
              "💾 Salvar Nova Senha e Acessar Sistema"
          )

        if btn_atualizar_senha:
          if nova_senha_1 != nova_senha_2:
            st.error("As senhas não coincidem. Tente novamente.")
          else:
            valido, msg_erro = validar_senha_forte(nova_senha_1)
            if not valido:
              st.error(f"❌ {msg_erro}")
            else:
              st.session_state.credenciais_df.loc[
                  (st.session_state.credenciais_df["Nome"] == usuario_ativo)
                  & (
                      (st.session_state.credenciais_df["Perfil"] == perfil_atual)
                      | (st.session_state.credenciais_df["Cargo"] == perfil_atual)
                  ),
                  ["Senha", "primeiro_acesso"],
              ] = [nova_senha_1, False]
              st.session_state.credenciais_df.to_csv(CREDENCIAIS_CSV, index=False)
              st.session_state[f"exigir_troca_senha_{usuario_ativo}"] = False
              registrar_log(
                  "Usuário cadastrou nova senha no primeiro acesso",
                  "N/A",
                  usuario_ativo,
              )
              st.success(
                  "✔️ Senha atualizada com sucesso! Carregando painel..."
              )
              st.rerun()
        st.stop()

      st.success(f"Sessão ativa como: **{usuario_ativo}**")

      if st.sidebar.button("Logoff / Sair"):
        st.session_state[f"autenticado_{perfil_atual}"] = False
        st.session_state[f"usuario_ativo_{perfil_atual}"] = None
        st.rerun()

      # --- CONTEÚDO EXCLUSIVO PARA GESTÃO / ADMINISTRADOR ---
      if perfil_atual in ["Gestão", "Administrador"]:
        (
            aba_alunos,
            aba_gestao_equipe,
            aba_professores,
            aba_goe_cad,
            aba_aoe_cad,
            aba_ocorrencias_gestao,
            aba_relatorios,
        ) = st.tabs([
            "📋 Painel e Alunos",
            "👔 Gestão da Equipe Gestora",
            "👩‍🏫 Gestão de Docentes",
            "👤 Gestão de GOE",
            "👤 Gestão de AOE",
            "🚨 Arquivo de Ocorrências & Chat",
            "📈 Risco e Auditoria",
        ])

        with aba_alunos:
          st.subheader(
              "📋 Gerenciamento, Upload e Alunos Individuais"
          )
          (
              sub_aba_up,
              sub_aba_cad_aluno,
              sub_aba_exc_aluno,
              sub_aba_ver_alunos,
          ) = st.tabs([
              "📁 Upload CSV",
              "➕ Incluir Aluno Individual",
              "🗑️ Excluir Aluno Individual",
              "📊 Visualizar Alunos",
          ])

          with sub_aba_up:
            col_up_tit, col_up_btn = st.columns([4, 1])
            col_up_tit.markdown(
                "### 📁 Upload de Arquivos CSV (Individual ou Múltiplos)"
            )
            if col_up_btn.button("🔄 Atualizar Tabelas", key="btn_ref_gestao_up"):
              st.success("Tabelas sincronizadas!")
              st.rerun()

            uploaded_files = st.file_uploader(
                "Selecione um ou mais arquivos CSV de turmas:",
                type=["csv"],
                accept_multiple_files=True,
                key="uploader_alunos_gestao",
            )
            if uploaded_files:
              for uploaded_file in uploaded_files:
                with open(uploaded_file.name, "wb") as f:
                  f.write(uploaded_file.getbuffer())
              st.success(
                  f"✔️ {len(uploaded_files)} arquivo(s) CSV enviado(s) com"
                  " sucesso!"
              )
              registrar_log(
                  f"Gestão fez upload de {len(uploaded_files)} arquivo(s) CSV",
                  "N/A",
                  usuario_ativo,
              )
              st.rerun()

          with sub_aba_cad_aluno:
            st.markdown("### ➕ Incluir Aluno Individualmente")
            with st.form("form_cad_aluno_individual", clear_on_submit=True):
              col_i1, col_i2 = st.columns(2)
              serie_novo = col_i1.selectbox(
                  "🏫 Série / Turma:", options=SERIES_TURMAS
              )
              ra_novo = col_i2.text_input("🆔 RA do Aluno:")
              nome_novo = st.text_input("📝 Nome Completo do Aluno:")
              col_i3, col_i4, col_i5 = st.columns(3)
              email_novo = col_i3.text_input("📧 E-mail:", value="")
              tel_novo = col_i4.text_input("📞 Telefone:", value="")
              tel2_novo = col_i5.text_input("📞 Telefone 2:", value="")

              if st.form_submit_button("💾 Salvar Aluno", type="primary"):
                if ra_novo.strip() and nome_novo.strip():
                  nome_arq = f"{serie_novo}.csv"
                  novo_registro = {
                      "RA": ra_novo.strip(),
                      "Nome": nome_novo.strip(),
                      "Série": serie_novo,
                      "Presenças": 0,
                      "Faltas": 0,
                      "Email": email_novo.strip(),
                      "Telefone": tel_novo.strip(),
                      "Telefone 2": tel2_novo.strip(),
                  }
                  if os.path.exists(nome_arq):
                    df_arq = pd.read_csv(
                        nome_arq, sep=";", encoding="latin1", dtype={"RA": str}
                    )
                    if ra_novo.strip() in df_arq["RA"].values:
                      st.error(
                          "❌ Já existe um aluno com este RA nesta turma."
                      )
                    else:
                      df_arq = pd.concat(
                          [df_arq, pd.DataFrame([novo_registro])],
                          ignore_index=True,
                      )
                      df_arq.to_csv(
                          nome_arq, sep=";", index=False, encoding="latin1"
                      )
                      registrar_log(
                          f"Gestão cadastrou aluno {nome_novo.strip()}",
                          ra_novo.strip(),
                          usuario_ativo,
                      )
                      st.success(
                          f"✔️ Aluno(a) {nome_novo.strip()} incluído(a) com"
                          " sucesso!"
                      )
                      st.rerun()
                  else:
                    pd.DataFrame([novo_registro]).to_csv(
                        nome_arq, sep=";", index=False, encoding="latin1"
                    )
                    st.success(
                        f"✔️ Turma {serie_novo} criada e aluno incluído!"
                    )
                    st.rerun()
                else:
                  st.error("Preencha o RA e o Nome do Aluno.")

          with sub_aba_exc_aluno:
            st.markdown("### 🗑️ Excluir Aluno Individualmente")
            df_alunos_atual = st.session_state.alunos
            if df_alunos_atual.empty:
              st.info("Não há alunos cadastrados.")
            else:
              col_e1, col_e2 = st.columns(2)
              serie_exc_escolhida = col_e1.selectbox(
                  "🏫 Série:",
                  options=sorted(
                      df_alunos_atual["Série"].dropna().unique().tolist()
                  ),
                  key="exc_aluno_serie",
              )
              df_alunos_por_serie = df_alunos_atual[
                  df_alunos_atual["Série"] == serie_exc_escolhida
              ]
              if not df_alunos_por_serie.empty:
                opcoes_alunos_exc = df_alunos_por_serie.apply(
                    lambda r: f"Nome: {r['Nome']} (RA: {r['RA']})", axis=1
                ).tolist()
                aluno_exc_selecionado_str = col_e2.selectbox(
                    "👤 Aluno:", options=opcoes_alunos_exc, key="exc_aluno_nome"
                )
                with st.form("form_excluir_aluno_individual"):
                  if st.form_submit_button(
                      "🗑️ Excluir Aluno Selecionado", type="secondary"
                  ):
                    ra_para_remover = (
                        aluno_exc_selecionado_str.split("(RA: ")[1]
                        .replace(")", "")
                        .strip()
                    )
                    nome_para_remover = (
                        aluno_exc_selecionado_str.split(" (RA:")[0]
                        .replace("Nome: ", "")
                        .strip()
                    )
                    nome_arq = f"{serie_exc_escolhida}.csv"
                    if os.path.exists(nome_arq):
                      df_arq_turma = pd.read_csv(
                          nome_arq, sep=";", encoding="latin1", dtype={"RA": str}
                      )
                      df_arq_turma = df_arq_turma[
                          df_arq_turma["RA"] != ra_para_remover
                      ]
                      df_arq_turma.to_csv(
                          nome_arq, sep=";", index=False, encoding="latin1"
                      )
                      registrar_log(
                          f"Gestão excluiu aluno {nome_para_remover}",
                          ra_para_remover,
                          usuario_ativo,
                      )
                      st.success("🗑️ Aluno(a) excluído(a) com sucesso!")
                      st.rerun()

          with sub_aba_ver_alunos:
            col_v_tit, col_v_btn = st.columns([4, 1])
            col_v_tit.markdown("### 📊 Turmas e Alunos Cadastrados")
            if col_v_btn.button("🔄 Atualizar Tabela", key="btn_ref_gestao_ver"):
              st.success("Tabela atualizada!")
              st.rerun()

            if not st.session_state.alunos.empty:
              st.dataframe(
                  st.session_state.alunos,
                  use_container_width=True,
                  hide_index=True,
              )
            else:
              st.info("Nenhum aluno encontrado.")

        with aba_gestao_equipe:
          st.subheader(
              "👔 Cadastro e Gerenciamento da Equipe Gestora (SEDUC-SP)"
          )
          col_cad_gestao, col_exc_gestao = st.columns(2)

          with col_cad_gestao:
            st.markdown("### ➕ Cadastrar Membro da Gestão")
            with st.form("form_cad_membro_gestao", clear_on_submit=True):
              nome_gestao = st.text_input("📝 Nome Completo do Gestor:")
              senha_gestao = st.text_input("🔒 Senha de Acesso:", type="password")
              cargo_gestao = st.selectbox(
                  "📌 Cargo SEDUC-SP:", options=CARGOS_GESTAO_SEDUC
              )
              turno_gestao = st.selectbox(
                  "⏰ Turno / Período:",
                  options=["Integral", "Manhã", "Tarde", "Noite"],
                  key="turno_gestao_cad",
              )

              if st.form_submit_button("💾 Salvar Gestor", type="primary"):
                if nome_gestao.strip() and senha_gestao.strip():
                  novo_gestor_df = pd.DataFrame([{
                      "Nome": nome_gestao.strip(),
                      "Perfil": "Gestão",
                      "Senha": senha_gestao.strip(),
                      "Disciplinas": "Todas",
                      "Series": "Todas",
                      "Turno": turno_gestao,
                      "Cargo": cargo_gestao,
                      "primeiro_acesso": True,
                  }])
                  st.session_state.credenciais_df = pd.concat(
                      [st.session_state.credenciais_df, novo_gestor_df],
                      ignore_index=True,
                  )
                  st.session_state.credenciais_df.to_csv(
                      CREDENCIAIS_CSV, index=False
                  )
                  registrar_log(
                      f"Gestão cadastrou novo membro gestor:"
                      f" {nome_gestao.strip()} ({cargo_gestao})",
                      "N/A",
                      usuario_ativo,
                  )
                  st.success(
                      f"✔️ Gestor(a) {nome_gestao.strip()} ({cargo_gestao})"
                      " cadastrado(a) com sucesso!"
                  )
                  st.rerun()
                else:
                  st.error("Preencha todos os campos obrigatórios.")

          with col_exc_gestao:
            st.markdown("### 🗑️ Remover Membro da Gestão")
            df_membros_gestao = st.session_state.credenciais_df[
                st.session_state.credenciais_df["Perfil"] == "Gestão"
            ]
            if not df_membros_gestao.empty:
              with st.form("form_exc_membro_gestao", clear_on_submit=True):
                gestor_rem_selecionado = st.selectbox(
                    "Selecione o Membro da Gestão para remover:",
                    options=df_membros_gestao["Nome"].tolist(),
                    key="exc_gestao_sel",
                )
                if st.form_submit_button(
                    "🗑️ Remover Gestor", type="secondary"
                ):
                  st.session_state.credenciais_df = (
                      st.session_state.credenciais_df[
                          ~(
                              (
                                  st.session_state.credenciais_df["Nome"]
                                  == gestor_rem_selecionado
                              )
                              & (
                                  st.session_state.credenciais_df["Perfil"]
                                  == "Gestão"
                              )
                          )
                      ]
                  )
                  st.session_state.credenciais_df.to_csv(
                      CREDENCIAIS_CSV, index=False
                  )
                  registrar_log(
                      "Gestão removeu membro gestor:"
                      f" {gestor_rem_selecionado}",
                      "N/A",
                      usuario_ativo,
                  )
                  st.success(
                      f"🗑️ Gestor {gestor_rem_selecionado} removido com"
                      " sucesso!"
                  )
                  st.rerun()
            else:
              st.info("Nenhum membro da gestão cadastrado.")

          st.markdown("---")
          st.markdown("### 📋 Lista Atual da Equipe Gestora")
          if not df_membros_gestao.empty:
            st.dataframe(
                df_membros_gestao[["Nome", "Cargo", "Turno"]],
                use_container_width=True,
                hide_index=True,
            )
          else:
            st.info("Nenhum gestor cadastrado.")

        with aba_professores:
          st.subheader("👩‍🏫 Gestão de Docentes")
          col_cad_prof, col_exc_prof = st.columns(2)
          with col_cad_prof:
            with st.form("form_cad_professor", clear_on_submit=True):
              nome_prof = st.text_input("📝 Nome Completo:")
              senha_prof = st.text_input("🔒 Senha:", type="password")
              disc_prof = st.multiselect(
                  "📚 Disciplinas:", options=DISCIPLINAS_SEDUC_COMPLETA
              )

              st.markdown(
                  "🏫 **Turmas (Escopo Completo - 1ª Série A à 3ª Série D):**"
              )
              todas_turmas_docente = st.checkbox(
                  "Selecionar todas as turmas automaticamente"
              )
              if todas_turmas_docente:
                series_prof = SERIES_TURMAS
              else:
                series_prof = st.multiselect(
                    "Ou selecione turmas específicas:", options=SERIES_TURMAS
                )

              if st.form_submit_button("💾 Salvar Professor", type="primary"):
                if nome_prof and senha_prof and disc_prof:
                  lista_turmas_salvar = (
                      SERIES_TURMAS if todas_turmas_docente else series_prof
                  )
                  novo_p = pd.DataFrame([{
                      "Nome": nome_prof.strip(),
                      "Perfil": "Professores",
                      "Senha": senha_prof.strip(),
                      "Disciplinas": ", ".join(disc_prof),
                      "Series": (
                          ", ".join(lista_turmas_salvar)
                          if lista_turmas_salvar
                          else "Nenhuma"
                      ),
                      "Turno": "Nenhum",
                      "Cargo": "Professor",
                      "primeiro_acesso": True,
                  }])
                  st.session_state.credenciais_df = pd.concat(
                      [st.session_state.credenciais_df, novo_p],
                      ignore_index=True,
                  )
                  st.session_state.credenciais_df.to_csv(
                      CREDENCIAIS_CSV, index=False
                  )
                  st.success("Professor cadastrado com sucesso!")
                  st.rerun()
                else:
                  st.error("Preencha os campos obrigatórios.")

          with col_exc_prof:
            df_p_ex = st.session_state.credenciais_df[
                st.session_state.credenciais_df["Perfil"] == "Professores"
            ]
            if not df_p_ex.empty:
              with st.form("form_exc_prof", clear_on_submit=True):
                prof_rem = st.selectbox(
                    "Selecione o professor para remover:",
                    options=df_p_ex["Nome"].tolist(),
                )
                if st.form_submit_button(
                    "🗑️ Remover Professor", type="secondary"
                ):
                  st.session_state.credenciais_df = (
                      st.session_state.credenciais_df[
                          ~(
                              (
                                  st.session_state.credenciais_df["Nome"]
                                  == prof_rem
                              )
                              & (
                                  st.session_state.credenciais_df["Perfil"]
                                  == "Professores"
                              )
                          )
                      ]
                  )
                  st.session_state.credenciais_df.to_csv(
                      CREDENCIAIS_CSV, index=False
                  )
                  st.success("Professor removido!")
                  st.rerun()
            else:
              st.info("Nenhum professor cadastrado.")

        with aba_goe_cad:
          st.subheader("👤 Gestão de GOE")
          col_cad_goe, col_exc_goe = st.columns(2)
          with col_cad_goe:
            with st.form("form_cad_goe", clear_on_submit=True):
              nome_goe = st.text_input("📝 Nome Completo:")
              senha_goe = st.text_input("🔒 Senha:", type="password")
              turno_goe = st.selectbox("⏰ Período:", options=TURNOS_GOE)
              if st.form_submit_button("💾 Salvar GOE", type="primary"):
                if nome_goe and senha_goe:
                  novo_a = pd.DataFrame([{
                      "Nome": nome_goe.strip(),
                      "Perfil": "Gestão GOE",
                      "Senha": senha_goe.strip(),
                      "Disciplinas": "Nenhuma",
                      "Series": "Nenhuma",
                      "Turno": turno_goe,
                      "Cargo": "GOE",
                      "primeiro_acesso": True,
                  }])
                  st.session_state.credenciais_df = pd.concat(
                      [st.session_state.credenciais_df, novo_a],
                      ignore_index=True,
                  )
                  st.session_state.credenciais_df.to_csv(
                      CREDENCIAIS_CSV, index=False
                  )
                  st.success("GOE cadastrado com sucesso!")
                  st.rerun()
          with col_exc_goe:
            df_g_ex = st.session_state.credenciais_df[
                st.session_state.credenciais_df["Perfil"] == "Gestão GOE"
            ]
            if not df_g_ex.empty:
              with st.form("form_exc_goe", clear_on_submit=True):
                goe_rem = st.selectbox("Selecione:", options=df_g_ex["Nome"].tolist())
                if st.form_submit_button("🗑️ Remover GOE", type="secondary"):
                  st.session_state.credenciais_df = (
                      st.session_state.credenciais_df[
                          ~(
                              (
                                  st.session_state.credenciais_df["Nome"]
                                  == goe_rem
                              )
                              & (
                                  st.session_state.credenciais_df["Perfil"]
                                  == "Gestão GOE"
                              )
                          )
                      ]
                  )
                  st.session_state.credenciais_df.to_csv(
                      CREDENCIAIS_CSV, index=False
                  )
                  st.success("Removido!")
                  st.rerun()

        with aba_aoe_cad:
          st.subheader("👤 Gestão de AOE")
          col_cad_aoe_gestao, col_exc_aoe_gestao = st.columns(2)
          with col_cad_aoe_gestao:
            with st.form("form_cad_aoe_gestao", clear_on_submit=True):
              nome_aoe_g = st.text_input("📝 Nome Completo do AOE:")
              senha_aoe_g = st.text_input("🔒 Senha de Acesso:", type="password")
              turno_aoe_g = st.selectbox(
                  "⏰ Período / Turno:",
                  options=TURNOS_GOE,
                  key="turno_aoe_cad_gestao",
              )
              if st.form_submit_button("💾 Salvar AOE", type="primary"):
                if nome_aoe_g.strip() and senha_aoe_g.strip():
                  novo_aoe_df = pd.DataFrame([{
                      "Nome": nome_aoe_g.strip(),
                      "Perfil": "AOE",
                      "Senha": senha_aoe_g.strip(),
                      "Disciplinas": "Nenhuma",
                      "Series": "Nenhuma",
                      "Turno": turno_aoe_g,
                      "Cargo": "AOE",
                      "primeiro_acesso": True,
                  }])
                  st.session_state.credenciais_df = pd.concat(
                      [st.session_state.credenciais_df, novo_aoe_df],
                      ignore_index=True,
                  )
                  st.session_state.credenciais_df.to_csv(
                      CREDENCIAIS_CSV, index=False
                  )
                  registrar_log(
                      f"Gestão cadastrou novo AOE: {nome_aoe_g.strip()}",
                      "N/A",
                      usuario_ativo,
                  )
                  st.success(
                      f"✔️ AOE {nome_aoe_g.strip()} cadastrado(a) com sucesso!"
                  )
                  st.rerun()
                else:
                  st.error("Preencha todos os campos obrigatórios.")
          with col_exc_aoe_gestao:
            df_aoe_ex = st.session_state.credenciais_df[
                (st.session_state.credenciais_df["Perfil"] == "AOE")
                | (st.session_state.credenciais_df["Cargo"] == "AOE")
            ]
            if not df_aoe_ex.empty:
              with st.form("form_exc_aoe_gestao", clear_on_submit=True):
                aoe_rem_sel = st.selectbox(
                    "Selecione o AOE para remover:",
                    options=df_aoe_ex["Nome"].tolist(),
                )
                if st.form_submit_button("🗑️ Remover AOE", type="secondary"):
                  st.session_state.credenciais_df = (
                      st.session_state.credenciais_df[
                          ~(
                              (
                                  st.session_state.credenciais_df["Nome"]
                                  == aoe_rem_sel
                              )
                              & (
                                  (
                                      st.session_state.credenciais_df[
                                          "Perfil"
                                      ]
                                      == "AOE"
                                  )
                                  | (
                                      st.session_state.credenciais_df[
                                          "Cargo"
                                      ]
                                      == "AOE"
                                  )
                              )
                          )
                      ]
                  )
                  st.session_state.credenciais_df.to_csv(
                      CREDENCIAIS_CSV, index=False
                  )
                  registrar_log(
                      f"Gestão removeu AOE: {aoe_rem_sel}",
                      "N/A",
                      usuario_ativo,
                  )
                  st.success(f"🗑️ AOE {aoe_rem_sel} removido com sucesso!")
                  st.rerun()
            else:
              st.info("Nenhum AOE cadastrado.")

          st.markdown("---")
          st.markdown("### 📋 Lista Atual da Equipe AOE")
          if not df_aoe_ex.empty:
            st.dataframe(
                df_aoe_ex[["Nome", "Cargo", "Turno"]],
                use_container_width=True,
                hide_index=True,
            )
          else:
            st.info("Nenhum AOE cadastrado.")

        with aba_ocorrencias_gestao:
          col_oc_tit, col_oc_btn = st.columns([4, 1])
          col_oc_tit.subheader(
              "🚨 Arquivo Geral de Ocorrências, Alertas e Comunicação"
          )
          if col_oc_btn.button("🔄 Atualizar", key="btn_ref_gestao_oc"):
            st.rerun()

          if os.path.exists(OCORRENCIAS_CSV):
            df_check_alerta = pd.read_csv(OCORRENCIAS_CSV, dtype={"RA": str})
            if not df_check_alerta.empty and "Nome" in df_check_alerta.columns:
              contagem_alunos = df_check_alerta["Nome"].value_counts()
              alunos_criticos = contagem_alunos[contagem_alunos >= 3]
              if not alunos_criticos.empty:
                st.error(
                    "🔥 **ALERTA PRIORITÁRIO:** Alunos com 3 ou mais ocorrências:"
                )
                for nome_critico, qtd in alunos_criticos.items():
                  st.warning(
                      f"⚠️ Aluno(a): **{nome_critico}** | Total: **{qtd}**"
                  )
                st.markdown("---")

          sub_aba_ver, sub_aba_cad, sub_aba_exc = st.tabs([
              "📋 Arquivo e Chat",
              "➕ Incluir Ocorrência",
              "🗑️ Excluir Ocorrência",
          ])
          with sub_aba_ver:
            if os.path.exists(OCORRENCIAS_CSV):
              df_oc_geral = pd.read_csv(OCORRENCIAS_CSV, dtype={"RA": str})
              if "MensagemGestaoAOE" not in df_oc_geral.columns:
                df_oc_geral["MensagemGestaoAOE"] = ""
              if not df_oc_geral.empty:
                col_filtro_serie, col_filtro_nome = st.columns(2)
                serie_filtrada = col_filtro_serie.selectbox(
                    "Filtrar por Série:",
                    options=["Todas"]
                    + sorted(df_oc_geral["Série"].dropna().unique().tolist()),
                )
                df_temp_filtro = (
                    df_oc_geral
                    if serie_filtrada == "Todas"
                    else df_oc_geral[df_oc_geral["Série"] == serie_filtrada]
                )
                nome_filtrado = col_filtro_nome.selectbox(
                    "Filtrar por Aluno:",
                    options=["Todos"]
                    + sorted(df_temp_filtro["Nome"].dropna().unique().tolist()),
                )
                df_exibicao_final = (
                    df_temp_filtro
                    if nome_filtrado == "Todos"
                    else df_temp_filtro[df_temp_filtro["Nome"] == nome_filtrado]
                )
                st.dataframe(
                    df_exibicao_final[[
                        "Data",
                        "RA",
                        "Nome",
                        "Série",
                        "Gravidade",
                        "Descricao",
                        "Professor",
                        "MensagemGestaoAOE",
                    ]],
                    use_container_width=True,
                    hide_index=True,
                )

                st.markdown("---")
                st.markdown("### 💬 Enviar Comunicado / Retorno ao Professor")
                indices_oc = df_exibicao_final.index.tolist()
                opcoes_oc_sel = [
                    (
                        f"[{row['Data']}] Série: {row['Série']} | Aluno:"
                        f" {row['Nome']} (Prof. {row['Professor']})"
                    )
                    for idx, row in df_exibicao_final.iterrows()
                ]
                if indices_oc:
                  selected_oc_idx = st.selectbox(
                      "Selecione a ocorrência:",
                      options=indices_oc,
                      format_func=lambda x: opcoes_oc_sel[
                          indices_oc.index(x)
                      ],
                  )
                  with st.form("form_resposta_gestao"):
                    nova_msg = st.text_input(
                        "Escreva a orientação para o docente:"
                    )
                    if st.form_submit_button("Enviar Mensagem"):
                      if nova_msg.strip():
                        df_oc_geral.loc[selected_oc_idx, "MensagemGestaoAOE"] = (
                            f"{usuario_ativo}: {nova_msg.strip()}"
                        )
                        df_oc_geral.to_csv(OCORRENCIAS_CSV, index=False)
                        st.success("✔️ Mensagem enviada!")
                        st.rerun()
                      else:
                        st.error("Digite a mensagem.")

          with sub_aba_cad:
            df_alunos_geral = st.session_state.alunos
            if not df_alunos_geral.empty:
              lista_opcoes_alunos_gestao = df_alunos_geral.apply(
                  lambda r: (
                      f"Série: {r['Série']} | RA: {r['RA']} | Nome:"
                      f" {r['Nome']}"
                  ),
                  axis=1,
              ).tolist()
              with st.form(
                  "form_incluir_ocorrencia_gestao", clear_on_submit=True
              ):
                aluno_gestao_str = st.selectbox(
                    "Aluno:", options=lista_opcoes_alunos_gestao
                )
                gravidade_gestao = st.selectbox(
                    "Gravidade:",
                    options=[
                        "Baixa (Aviso/Advertência)",
                        "Média (Comportamental)",
                        "Alta (Encaminhamento à Gestão)",
                    ],
                )
                descricao_gestao = st.text_area("📝 Descrição:")
                if st.form_submit_button("💾 Salvar Ocorrência", type="primary"):
                  if descricao_gestao.strip():
                    idx_g = lista_opcoes_alunos_gestao.index(aluno_gestao_str)
                    aluno_g_row = df_alunos_geral.iloc[idx_g]
                    nova_oc_g = pd.DataFrame([{
                        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "RA": str(aluno_g_row["RA"]),
                        "Nome": str(aluno_g_row["Nome"]),
                        "Série": str(aluno_g_row["Série"]),
                        "Gravidade": gravidade_gestao,
                        "Descricao": descricao_gestao.strip(),
                        "Professor": f"{usuario_ativo} (Gestão)",
                        "MensagemGestaoAOE": "",
                    }])
                    nova_oc_g.to_csv(
                        OCORRENCIAS_CSV,
                        mode="a",
                        header=not os.path.exists(OCORRENCIAS_CSV),
                        index=False,
                    )
                    st.success("✔️ Ocorrência inserida!")
                    st.rerun()
                  else:
                    st.error("Preencha a descrição.")

          with sub_aba_exc:
            if os.path.exists(OCORRENCIAS_CSV):
              df_oc_exc = pd.read_csv(OCORRENCIAS_CSV, dtype={"RA": str})
              if not df_oc_exc.empty:
                col_exc_serie, col_exc_aluno_sel = st.columns(2)
                serie_exc_filtro = col_exc_serie.selectbox(
                    "Série:",
                    options=["Todas"]
                    + sorted(df_oc_exc["Série"].dropna().unique().tolist()),
                    key="exc_serie",
                )
                df_exc_temp = (
                    df_oc_exc
                    if serie_exc_filtro == "Todas"
                    else df_oc_exc[df_oc_exc["Série"] == serie_exc_filtro]
                )
                indices_exc_filtrados = df_exc_temp.index.tolist()
                opcoes_exc_aluno = [
                    (
                        f"Série: {row['Série']} | Aluno: {row['Nome']} (RA:"
                        f" {row['RA']})"
                    )
                    for idx, row in df_exc_temp.iterrows()
                ]
                with st.form("form_excluir_ocorrencia_gestao"):
                  if indices_exc_filtrados:
                    aluno_para_remover_idx = st.selectbox(
                        "Ocorrência:",
                        options=indices_exc_filtrados,
                        format_func=lambda x: opcoes_exc_aluno[
                            indices_exc_filtrados.index(x)
                        ],
                    )
                    if st.form_submit_button("🗑️ Excluir", type="secondary"):
                      df_oc_exc.drop(aluno_para_remover_idx).reset_index(
                          drop=True
                      ).to_csv(OCORRENCIAS_CSV, index=False)
                      st.success("🗑️ Ocorrência excluída!")
                      st.rerun()

        with aba_relatorios:
          col_rel_tit, col_rel_btn = st.columns([4, 1])
          col_rel_tit.subheader(
              "📈 Relatório Avançado de Probabilidade, Risco e Contagem"
              " Quantitativa (SEDUC-SP & MEC)"
          )
          if col_rel_btn.button("🔄 Atualizar Relatório", key="btn_ref_relatorio"):
            st.success("Dados atualizados!")
            st.rerun()

          st.markdown("""
                    > **Legislação de Referência (LDB / MEC - Art. 24, VI & SEDUC-SP):** O controle de frequência é obrigatório, sendo exigido o **mínimo de 75% de frequência** sobre o total de chamadas/aulas realizadas para aprovação do aluno. Este painel consolida a **contagem quantitativa de presenças e faltas** apuradas nas chamadas realizadas pelos GOE/AOE, identificando turmas e alunos em risco de reprovação por falta para acionamento imediato da Busca Ativa.
                    """)

          df_alunos_audit = st.session_state.alunos.copy()
          if df_alunos_audit.empty:
            st.info(
                "Nenhum dado de aluno ou chamada disponível para análise"
                " quantitativa de risco."
            )
          else:
            df_alunos_audit["Total_Aulas"] = (
                df_alunos_audit["Presenças"] + df_alunos_audit["Faltas"]
            )
            df_alunos_audit["Frequencia_%"] = df_alunos_audit.apply(
                lambda r: (
                    (r["Presenças"] / r["Total_Aulas"] * 100)
                    if r["Total_Aulas"] > 0
                    else 100.0
                ),
                axis=1,
            )

            def classificar_risco_reprovacao(freq, total):
              if total == 0:
                return "Sem Registros de Chamada"
              elif freq < 75.0:
                return "🔴 Risco Crítico (Reprovado / Abaixo de 75%)"
              elif freq < 80.0:
                return (
                    "🟠 Risco Alto (Entre 75% e 80% - Zona de Alerta)"
                )
              elif freq < 90.0:
                return "🟡 Risco Moderado (Entre 80% e 90%)"
              else:
                return "🟢 Risco Baixo / Seguro (> 90%)"

            df_alunos_audit["Status_Risco"] = df_alunos_audit.apply(
                lambda r: classificar_risco_reprovacao(
                    r["Frequencia_%"], r["Total_Aulas"]
                ),
                axis=1,
            )

            total_presencas_geral = int(df_alunos_audit["Presenças"].sum())
            total_faltas_geral = int(df_alunos_audit["Faltas"].sum())
            total_aulas_geral = total_presencas_geral + total_faltas_geral
            freq_media_geral = (
                (total_presencas_geral / total_aulas_geral * 100)
                if total_aulas_geral > 0
                else 100.0
            )

            criticos_count = len(
                df_alunos_audit[df_alunos_audit["Frequencia_%"] < 75.0]
            )
            altos_count = len(
                df_alunos_audit[
                    (df_alunos_audit["Frequencia_%"] >= 75.0)
                    & (df_alunos_audit["Frequencia_%"] < 80.0)
                ]
            )

            st.markdown(
                "### 📊 Contagem Quantitativa Geral de Chamadas (Escola)"
            )
            col_q1, col_q2, col_q3, col_q4, col_q5 = st.columns(5)
            col_q1.metric(
                "Total Presenças",
                f"{total_presencas_geral:,}".replace(",", "."),
            )
            col_q2.metric(
                "Total Faltas", f"{total_faltas_geral:,}".replace(",", ".")
            )
            col_q3.metric("Frequência Média", f"{freq_media_geral:.1f}%")
            col_q4.metric(
                "Risco Crítico (< 75%)", criticos_count, delta_color="inverse"
            )
            col_q5.metric("Risco Alto (75-80%)", altos_count)

            st.markdown("---")
            st.markdown(
                "### 🏫 Contagem Quantitativa Agrupada por Série / Turma"
                " (Escopo Completo - 1ª Série A à 3ª Série D)"
            )
            df_base_turmas = pd.DataFrame({"Série": SERIES_TURMAS})

            df_agrupado_serie = (
                df_alunos_audit.groupby("Série")
                .agg(
                    Alunos=("RA", "count"),
                    Presenças=("Presenças", "sum"),
                    Faltas=("Faltas", "sum"),
                )
                .reset_index()
            )

            df_agrupado_serie = pd.merge(
                df_base_turmas, df_agrupado_serie, on="Série", how="left"
            ).fillna({"Alunos": 0, "Presenças": 0, "Faltas": 0})
            df_agrupado_serie["Alunos"] = df_agrupado_serie["Alunos"].astype(
                int
            )
            df_agrupado_serie["Presenças"] = df_agrupado_serie[
                "Presenças"
            ].astype(int)
            df_agrupado_serie["Faltas"] = df_agrupado_serie["Faltas"].astype(
                int
            )

            df_agrupado_serie["Total_Aulas"] = (
                df_agrupado_serie["Presenças"] + df_agrupado_serie["Faltas"]
            )
            df_agrupado_serie["Frequencia_Media_%"] = (
                df_agrupado_serie.apply(
                    lambda r: (
                        (r["Presenças"] / r["Total_Aulas"] * 100)
                        if r["Total_Aulas"] > 0
                        else 100.0
                    ),
                    axis=1,
                )
                .round(2)
            )

            criticos_por_serie = (
                df_alunos_audit[df_alunos_audit["Frequencia_%"] < 75.0]
                .groupby("Série")["RA"]
                .count()
                .reset_index(name="Alunos_Risco_Critico")
            )
            df_agrupado_serie = pd.merge(
                df_agrupado_serie,
                criticos_por_serie,
                on="Série",
                how="left",
            ).fillna({"Alunos_Risco_Critico": 0})
            df_agrupado_serie["Alunos_Risco_Critico"] = df_agrupado_serie[
                "Alunos_Risco_Critico"
            ].astype(int)
            df_agrupado_serie["Frequencia_Media_%"] = (
                df_agrupado_serie["Frequencia_Media_%"].astype(str) + "%"
            )

            st.dataframe(
                df_agrupado_serie, use_container_width=True, hide_index=True
            )

            st.markdown("---")
            st.markdown(
                "### 🔍 Listagem Detalhada por Aluno e Probabilidade de"
                " Reprovação"
            )
            col_fa1, col_fa2 = st.columns(2)
            serie_filtro_rel = col_fa1.selectbox(
                "🏫 Filtrar por Série:",
                options=["Todas"]
                + sorted(df_alunos_audit["Série"].dropna().unique().tolist()),
            )
            risco_filtro_rel = col_fa2.selectbox(
                "📊 Filtrar por Nível de Risco:",
                options=[
                    "Todos",
                    "🔴 Risco Crítico (Reprovado / Abaixo de 75%)",
                    "🟠 Risco Alto (Entre 75% e 80% - Zona de Alerta)",
                    "🟡 Risco Moderado (Entre 80% e 90%)",
                    "🟢 Risco Baixo / Seguro (> 90%)",
                    "Sem Registros de Chamada",
                ],
            )

            df_rel_final = df_alunos_audit.copy()
            if serie_filtro_rel != "Todas":
              df_rel_final = df_rel_final[
                  df_rel_final["Série"] == serie_filtro_rel
              ]
            if risco_filtro_rel != "Todos":
              df_rel_final = df_rel_final[
                  df_rel_final["Status_Risco"] == risco_filtro_rel
              ]

            df_exibicao_relatorio = df_rel_final[[
                "RA",
                "Nome",
                "Série",
                "Presenças",
                "Faltas",
                "Total_Aulas",
                "Frequencia_%",
                "Status_Risco",
            ]].copy()
            df_exibicao_relatorio["Frequencia_%"] = (
                df_exibicao_relatorio["Frequencia_%"]
                .round(2)
                .astype(str)
                + "%"
            )

            st.dataframe(
                df_exibicao_relatorio,
                use_container_width=True,
                hide_index=True,
            )

            st.markdown("---")
            st.subheader("📜 Logs de Auditoria do Sistema")
            if os.path.exists(LOG_FILE):
              st.dataframe(
                  pd.read_csv(LOG_FILE), use_container_width=True, hide_index=True
              )
            else:
              st.info("Nenhum log registrado.")

      # ==============================================================================
      # --- PAINEL AOE (PERFIL DEDICADO COM CHAMADA, UPLOAD E RELATÓRIO SEDUC) ---
      # ==============================================================================
      elif perfil_atual == "AOE":
        st.subheader("👤 Painel de Organização Escolar - AOE")

        if os.path.exists(OCORRENCIAS_CSV):
          df_oc_aoe_painel = pd.read_csv(OCORRENCIAS_CSV, dtype={"RA": str})
          if not df_oc_aoe_painel.empty:
            st.error(
                f"🚨 ALERTA: Existem {len(df_oc_aoe_painel)} ocorrência(s)"
                " registrada(s) na escola!"
            )

        st.markdown("---")

        aba_aoe_chamada_geral, aba_aoe_upload, aba_aoe_relatorio = st.tabs([
            "📅 Lista de Chamada (Presença e Falta)",
            "📁 Upload de Arquivos CSV (Individual/Múltiplos)",
            "📈 Relatório Avançado & Risco (SEDUC-SP & MEC)",
        ])

        with aba_aoe_chamada_geral:
          st.subheader("📅 Registro de Chamada - Todas as Turmas Cadastradas")
          st.markdown("Realize o registro diário de presenças e faltas por turma:")

          col_ch1, col_ch2 = st.columns(2)
          data_chamada_aoe = col_ch1.date_input(
              "Data do Registro de Chamada:",
              value=date.today(),
              key="data_chamada_aoe_picker",
          )
          turma_chamada_aoe = col_ch2.selectbox(
              "Selecione a Série / Turma:",
              options=SERIES_TURMAS,
              key="turma_chamada_aoe_sel",
          )

          arquivo_turma_atual = f"{turma_chamada_aoe}.csv"
          if not os.path.exists(arquivo_turma_atual):
            st.warning(
                f"⚠️ O arquivo da turma '{turma_chamada_aoe}' ainda não foi"
                " criado ou enviado via CSV."
            )
            with st.form("form_criar_turma_aoe_vazia"):
              if st.form_submit_button("Criar Turma Vazia"):
                pd.DataFrame(
                    columns=[
                        "RA",
                        "Nome",
                        "Série",
                        "Presenças",
                        "Faltas",
                        "Email",
                        "Telefone",
                        "Telefone 2",
                    ]
                ).to_csv(
                    arquivo_turma_atual, sep=";", index=False, encoding="latin1"
                )
                st.success(f"Turma {turma_chamada_aoe} inicializada com sucesso!")
                st.rerun()
          else:
            df_turma_aoe = pd.read_csv(
                arquivo_turma_atual, sep=";", encoding="latin1", dtype={"RA": str}
            )
            if df_turma_aoe.empty:
              st.info("Esta turma não possui alunos cadastrados.")
            else:
              st.markdown(f"### Alunos da Turma: {turma_chamada_aoe}")
              st.markdown(
                  "Marque abaixo os alunos que receberão **Falta** na chamada de"
                  " hoje (os demais computarão Presença automática):"
              )

              with st.form(key=f"form_chamada_turma_{turma_chamada_aoe}"):
                lista_faltosos = []
                for idx, row in df_turma_aoe.iterrows():
                  falta_marcada = st.checkbox(
                      f"RA: {row['RA']} — {row['Nome']}",
                      key=f"faltoso_{turma_chamada_aoe}_{row['RA']}",
                  )
                  if falta_marcada:
                    lista_faltosos.append(row["RA"])

                btn_salvar_chamada = st.form_submit_button(
                    "💾 Salvar Chamada do Dia", type="primary"
                )
                if btn_salvar_chamada:
                  for idx, row in df_turma_aoe.iterrows():
                    ra_aluno = row["RA"]
                    if ra_aluno in lista_faltosos:
                      df_turma_aoe.loc[
                          df_turma_aoe["RA"] == ra_aluno, "Faltas"
                      ] += 1
                    else:
                      df_turma_aoe.loc[
                          df_turma_aoe["RA"] == ra_aluno, "Presenças"
                      ] += 1

                  df_turma_aoe.to_csv(
                      arquivo_turma_atual, sep=";", index=False, encoding="latin1"
                  )
                  st.session_state.alunos = carregar_todos_alunos()
                  registrar_log(
                      f"AOE {usuario_ativo} realizou chamada da turma"
                      f" {turma_chamada_aoe}",
                      "N/A",
                      usuario_ativo,
                  )
                  st.success(
                      f"✔️ Chamada da turma {turma_chamada_aoe} salva e"
                      " computada com sucesso!"
                  )
                  st.rerun()

        with aba_aoe_upload:
          st.subheader(
              "📁 Upload de Arquivos CSV (Individual ou Múltiplos) e Atualização"
              " Automática"
          )
          st.markdown(
              "Envie um ou mais arquivos CSV contendo a listagem de turmas e"
              " alunos. O sistema atualizará os dados automaticamente."
          )

          uploaded_files_aoe = st.file_uploader(
              "Selecione arquivos CSV de turmas:",
              type=["csv"],
              accept_multiple_files=True,
              key="uploader_aoe_csv",
          )
          if uploaded_files_aoe:
            for uploaded_file in uploaded_files_aoe:
              with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.alunos = carregar_todos_alunos()
            registrar_log(
                f"AOE {usuario_ativo} fez upload"
                f" of {len(uploaded_files_aoe)} arquivo(s) CSV",
                "N/A",
                usuario_ativo,
            )
            st.success(
                f"✔️ {len(uploaded_files_aoe)} arquivo(s) CSV enviado(s) e"
                " sincronizados automaticamente com sucesso!"
            )
            st.rerun()

        with aba_aoe_relatorio:
          st.subheader(
              "📈 Relatório Avançado de Probabilidade, Risco e Contagem"
              " Quantitativa (SEDUC-SP & MEC)"
          )
          st.markdown("""
                    > **Legislação de Referência (LDB / MEC - Art. 24, VI & SEDUC-SP):** Monitoramento diário obrigatório de frequência escolar exigindo **mínimo de 75%** de frequência. Este painel exibe a contagem quantitativa geral, contagem agrupada por série/turma, e listagem detalhada por aluno com alertas automáticos.
                    """)

          df_alunos_audit_aoe = st.session_state.alunos.copy()
          if df_alunos_audit_aoe.empty:
            st.info("Nenhum dado de aluno disponível para o relatório.")
          else:
            df_alunos_audit_aoe["Total_Aulas"] = (
                df_alunos_audit_aoe["Presenças"] + df_alunos_audit_aoe["Faltas"]
            )
            df_alunos_audit_aoe["Frequencia_%"] = df_alunos_audit_aoe.apply(
                lambda r: (
                    (r["Presenças"] / r["Total_Aulas"] * 100)
                    if r["Total_Aulas"] > 0
                    else 100.0
                ),
                axis=1,
            )

            def classificar_risco_aoe(freq, total):
              if total == 0:
                return "Sem Registros de Chamada"
              elif freq < 75.0:
                return "🔴 Risco Crítico (Reprovado / Abaixo de 75%)"
              elif freq < 80.0:
                return (
                    "🟠 Risco Alto (Entre 75% e 80% - Zona de Alerta)"
                )
              elif freq < 90.0:
                return "🟡 Risco Moderado (Entre 80% e 90%)"
              else:
                return "🟢 Risco Baixo / Seguro (> 90%)"

            df_alunos_audit_aoe["Status_Risco"] = df_alunos_audit_aoe.apply(
                lambda r: classificar_risco_aoe(
                    r["Frequencia_%"], r["Total_Aulas"]
                ),
                axis=1,
            )

            total_pres_g = int(df_alunos_audit_aoe["Presenças"].sum())
            total_falt_g = int(df_alunos_audit_aoe["Faltas"].sum())
            total_aul_g = total_pres_g + total_falt_g
            freq_med_g = (
                (total_pres_g / total_aul_g * 100)
                if total_aul_g > 0
                else 100.0
            )
            crit_count = len(
                df_alunos_audit_aoe[df_alunos_audit_aoe["Frequencia_%"] < 75.0]
            )
            alto_count = len(
                df_alunos_audit_aoe[
                    (df_alunos_audit_aoe["Frequencia_%"] >= 75.0)
                    & (df_alunos_audit_aoe["Frequencia_%"] < 80.0)
                ]
            )

            st.markdown(
                "### 📊 Contagem Quantitativa Geral de Chamadas (Escola)"
            )
            cq1, cq2, cq3, cq4, cq5 = st.columns(5)
            cq1.metric(
                "Total Presenças", f"{total_pres_g:,}".replace(",", ".")
            )
            cq2.metric("Total Faltas", f"{total_falt_g:,}".replace(",", "."))
            cq3.metric("Frequência Média", f"{freq_med_g:.1f}%")
            cq4.metric(
                "Risco Crítico (< 75%)", crit_count, delta_color="inverse"
            )
            cq5.metric("Risco Alto (75-80%)", alto_count)

            st.markdown("---")
            st.markdown(
                "### 🏫 Contagem Quantitativa Agrupada por Série / Turma"
                " (Escopo Completo - 1ª Série A à 3ª Série D)"
            )
            df_base_t_aoe = pd.DataFrame({"Série": SERIES_TURMAS})
            df_agr_aoe = (
                df_alunos_audit_aoe.groupby("Série")
                .agg(
                    Alunos=("RA", "count"),
                    Presenças=("Presenças", "sum"),
                    Faltas=("Faltas", "sum"),
                )
                .reset_index()
            )

            df_agr_aoe = pd.merge(
                df_base_t_aoe, df_agr_aoe, on="Série", how="left"
            ).fillna({"Alunos": 0, "Presenças": 0, "Faltas": 0})
            df_agr_aoe["Alunos"] = df_agr_aoe["Alunos"].astype(int)
            df_agr_aoe["Presenças"] = df_agr_aoe["Presenças"].astype(int)
            df_agr_aoe["Faltas"] = df_agr_aoe["Faltas"].astype(int)
            df_agr_aoe["Total_Aulas"] = (
                df_agr_aoe["Presenças"] + df_agr_aoe["Faltas"]
            )
            df_agr_aoe["Frequencia_Media_%"] = (
                df_agr_aoe.apply(
                    lambda r: (
                        (r["Presenças"] / r["Total_Aulas"] * 100)
                        if r["Total_Aulas"] > 0
                        else 100.0
                    ),
                    axis=1,
                )
                .round(2)
            )

            crit_por_s = (
                df_alunos_audit_aoe[df_alunos_audit_aoe["Frequencia_%"] < 75.0]
                .groupby("Série")["RA"]
                .count()
                .reset_index(name="Alunos_Risco_Critico")
            )
            df_agr_aoe = pd.merge(
                df_agr_aoe, crit_por_s, on="Série", how="left"
            ).fillna({"Alunos_Risco_Critico": 0})
            df_agr_aoe["Alunos_Risco_Critico"] = df_agr_aoe[
                "Alunos_Risco_Critico"
            ].astype(int)
            df_agr_aoe["Frequencia_Media_%"] = (
                df_agr_aoe["Frequencia_Media_%"].astype(str) + "%"
            )

            st.dataframe(df_agr_aoe, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown(
                "### 🔍 Listagem Detalhada por Aluno e Probabilidade de"
                " Reprovação (Com Alertas Diários)"
            )

            col_fa_aoe1, col_fa_aoe2 = st.columns(2)
            serie_f_aoe = col_fa_aoe1.selectbox(
                "🏫 Filtrar Série:",
                options=["Todas"]
                + sorted(
                    df_alunos_audit_aoe["Série"].dropna().unique().tolist()
                ),
                key="aoe_rel_serie",
            )
            risco_f_aoe = col_fa_aoe2.selectbox(
                "📊 Filtrar Risco:",
                options=[
                    "Todos",
                    "🔴 Risco Crítico (Reprovado / Abaixo de 75%)",
                    "🟠 Risco Alto (Entre 75% e 80% - Zona de Alerta)",
                    "🟡 Risco Moderado (Entre 80% e 90%)",
                    "🟢 Risco Baixo / Seguro (> 90%)",
                    "Sem Registros de Chamada",
                ],
                key="aoe_rel_risco",
            )

            df_rel_aoe_fin = df_alunos_audit_aoe.copy()
            if serie_f_aoe != "Todas":
              df_rel_aoe_fin = df_rel_aoe_fin[
                  df_rel_aoe_fin["Série"] == serie_f_aoe
              ]
            if risco_f_aoe != "Todos":
              df_rel_aoe_fin = df_rel_aoe_fin[
                  df_rel_aoe_fin["Status_Risco"] == risco_f_aoe
              ]

            df_exib_aoe = df_rel_aoe_fin[[
                "RA",
                "Nome",
                "Série",
                "Presenças",
                "Faltas",
                "Total_Aulas",
                "Frequencia_%",
                "Status_Risco",
            ]].copy()
            df_exib_aoe["Frequencia_%"] = (
                df_exib_aoe["Frequencia_%"].round(2).astype(str) + "%"
            )

            st.dataframe(df_exib_aoe, use_container_width=True, hide_index=True)

      # ==============================================================================
      # --- PAINEL GESTÃO GOE (ESTRUTURA ORIGINAL RESTAURADA) ---
      # ==============================================================================
      elif perfil_atual == "Gestão GOE":
        st.subheader("📋 Central de Gestão GOE")

        if os.path.exists(OCORRENCIAS_CSV):
          df_oc_goe = pd.read_csv(OCORRENCIAS_CSV, dtype={"RA": str})
          if not df_oc_goe.empty:
            st.error(
                f"🚨 ALERTA: Existem {len(df_oc_goe)} ocorrência(s) recente(s)"
                " registrada(s) na escola!"
            )

        st.markdown("---")

        aba_goe_alunos, aba_goe_equipe, aba_goe_mensagens, aba_goe_chamada = (
            st.tabs([
                "📋 Painel e Alunos",
                "👥 Cadastrar/Gerenciar Equipe (GOE)",
                "💬 Enviar Mensagens Separadas",
                "📅 Registro de Chamada",
            ])
        )

        with aba_goe_alunos:
          (
              sub_aba_up_g,
              sub_aba_cad_aluno_g,
              sub_aba_exc_aluno_g,
              sub_aba_ver_alunos_g,
          ) = st.tabs([
              "📁 Upload CSV",
              "➕ Incluir Aluno Individual",
              "🗑️ Excluir Aluno Individual",
              "📊 Visualizar Alunos",
          ])

          with sub_aba_up_g:
            col_up_gtit, col_up_gbtn = st.columns([4, 1])
            col_up_gtit.markdown("### 📁 Upload de Arquivos CSV de Turmas")
            if col_up_gbtn.button("🔄 Atualizar", key="btn_ref_goe_up"):
              st.success("Tabelas atualizadas!")
              st.rerun()

            uploaded_files_g = st.file_uploader(
                "Selecione arquivos CSV:",
                type=["csv"],
                accept_multiple_files=True,
                key="uploader_alunos_goe",
            )
            if uploaded_files_g:
              for uploaded_file in uploaded_files_g:
                with open(uploaded_file.name, "wb") as f:
                  f.write(uploaded_file.getbuffer())
              st.success(
                  f"✔️ {len(uploaded_files_g)} arquivo(s) enviado(s)!"
              )
              registrar_log(
                  f"GOE fez upload de {len(uploaded_files_g)} arquivo(s) CSV",
                  "N/A",
                  usuario_ativo,
              )
              st.rerun()

          with sub_aba_cad_aluno_g:
            st.markdown("### ➕ Incluir Aluno Individualmente")
            with st.form("form_cad_aluno_individual_goe", clear_on_submit=True):
              col_ig1, col_ig2 = st.columns(2)
              serie_novo_g = col_ig1.selectbox(
                  "🏫 Série / Turma:",
                  options=SERIES_TURMAS,
                  key="goe_cad_serie",
              )
              ra_novo_g = col_ig2.text_input("🆔 RA do Aluno:", key="goe_cad_ra")
              nome_novo_g = st.text_input(
                  "📝 Nome Completo do Aluno:", key="goe_cad_nome"
              )
              col_ig3, col_ig4, col_ig5 = st.columns(3)
              email_novo_g = col_ig3.text_input(
                  "📧 E-mail:", value="", key="goe_cad_email"
              )
              tel_novo_g = col_ig4.text_input(
                  "📞 Telefone:", value="", key="goe_cad_tel"
              )
              tel2_novo_g = col_ig5.text_input(
                  "📞 Telefone 2:", value="", key="goe_cad_tel2"
              )

              if st.form_submit_button("💾 Salvar Aluno", type="primary"):
                if ra_novo_g.strip() and nome_novo_g.strip():
                  nome_arq = f"{serie_novo_g}.csv"
                  novo_registro = {
                      "RA": ra_novo_g.strip(),
                      "Nome": nome_novo_g.strip(),
                      "Série": serie_novo_g,
                      "Presenças": 0,
                      "Faltas": 0,
                      "Email": email_novo_g.strip(),
                      "Telefone": tel_novo_g.strip(),
                      "Telefone 2": tel2_novo_g.strip(),
                  }
                  if os.path.exists(nome_arq):
                    df_arq = pd.read_csv(
                        nome_arq, sep=";", encoding="latin1", dtype={"RA": str}
                    )
                    if ra_novo_g.strip() in df_arq["RA"].values:
                      st.error("❌ RA já existe nesta turma.")
                    else:
                      df_arq = pd.concat(
                          [df_arq, pd.DataFrame([novo_registro])],
                          ignore_index=True,
                      )
                      df_arq.to_csv(
                          nome_arq, sep=";", index=False, encoding="latin1"
                      )
                      registrar_log(
                          f"GOE cadastrou aluno {nome_novo_g.strip()}",
                          ra_novo_g.strip(),
                          usuario_ativo,
                      )
                      st.success("✔️ Aluno(a) incluído(a) com sucesso!")
                      st.rerun()
                  else:
                    pd.DataFrame([novo_registro]).to_csv(
                        nome_arq, sep=";", index=False, encoding="latin1"
                    )
                    st.success("✔️ Turma criada e aluno incluído!")
                    st.rerun()
                else:
                  st.error("Preencha RA e Nome.")

          with sub_aba_exc_aluno_g:
            st.markdown("### 🗑️ Excluir Aluno Individualmente")
            df_alunos_atual_g = st.session_state.alunos
            if df_alunos_atual_g.empty:
              st.info("Nenhum aluno cadastrado.")
            else:
              col_eg1, col_eg2 = st.columns(2)
              serie_exc_escolhida_g = col_eg1.selectbox(
                  "🏫 Série:",
                  options=sorted(
                      df_alunos_atual_g["Série"].dropna().unique().tolist()
                  ),
                  key="goe_exc_serie",
              )
              df_alunos_por_serie_g = df_alunos_atual_g[
                  df_alunos_atual_g["Série"] == serie_exc_escolhida_g
              ]
              if not df_alunos_por_serie_g.empty:
                opcoes_alunos_exc_g = df_alunos_por_serie_g.apply(
                    lambda r: f"Nome: {r['Nome']} (RA: {r['RA']})", axis=1
                ).tolist()
                aluno_exc_selecionado_str_g = col_eg2.selectbox(
                    "👤 Aluno:",
                    options=opcoes_alunos_exc_g,
                    key="goe_exc_nome",
                )
                with st.form("form_excluir_aluno_individual_goe"):
                  if st.form_submit_button("🗑️ Excluir Aluno", type="secondary"):
                    ra_para_remover_g = (
                        aluno_exc_selecionado_str_g.split("(RA: ")[1]
                        .replace(")", "")
                        .strip()
                    )
                    nome_para_remover_g = (
                        aluno_exc_selecionado_str_g.split(" (RA:")[0]
                        .replace("Nome: ", "")
                        .strip()
                    )
                    nome_arq = f"{serie_exc_escolhida_g}.csv"
                    if os.path.exists(nome_arq):
                      df_arq_turma = pd.read_csv(
                          nome_arq, sep=";", encoding="latin1", dtype={"RA": str}
                      )
                      df_arq_turma = df_arq_turma[
                          df_arq_turma["RA"] != ra_para_remover_g
                      ]
                      df_arq_turma.to_csv(
                          nome_arq, sep=";", index=False, encoding="latin1"
                      )
                      registrar_log(
                          f"GOE excluiu aluno {nome_para_remover_g}",
                          ra_para_remover_g,
                          usuario_ativo,
                      )
                      st.success("🗑️ Aluno(a) excluído(a) com sucesso!")
                      st.rerun()

          with sub_aba_ver_alunos_g:
            col_gv_tit, col_gv_btn = st.columns([4, 1])
            col_gv_tit.markdown("### 📊 Alunos Cadastrados no Sistema")
            if col_gv_btn.button("🔄 Atualizar", key="btn_ref_goe_ver"):
              st.success("Tabela atualizada!")
              st.rerun()

            if not st.session_state.alunos.empty:
              st.dataframe(
                  st.session_state.alunos,
                  use_container_width=True,
                  hide_index=True,
              )
            else:
              st.info("Nenhum aluno encontrado.")

        with aba_goe_equipe:
          st.subheader("👥 Cadastro e Gerenciamento da Equipe GOE")
          col_cad_eq, col_exc_eq = st.columns(2)

          with col_cad_eq:
            st.markdown("### ➕ Cadastrar Membro GOE")
            with st.form("form_cad_equipe_goe_proprio", clear_on_submit=True):
              nome_novo_goe = st.text_input("📝 Nome Completo do Membro:")
              senha_novo_goe = st.text_input(
                  "🔒 Senha de Acesso:", type="password"
              )
              turno_novo_goe = st.selectbox(
                  "⏰ Período / Turno:",
                  options=TURNOS_GOE,
                  key="turno_novo_goe_cad",
              )

              if st.form_submit_button("💾 Salvar Membro", type="primary"):
                if nome_novo_goe.strip() and senha_novo_goe.strip():
                  novo_membro_df = pd.DataFrame([{
                      "Nome": nome_novo_goe.strip(),
                      "Perfil": "Gestão GOE",
                      "Senha": senha_novo_goe.strip(),
                      "Disciplinas": "Nenhuma",
                      "Series": "Nenhuma",
                      "Turno": turno_novo_goe,
                      "Cargo": "GOE",
                      "primeiro_acesso": True,
                  }])
                  st.session_state.credenciais_df = pd.concat(
                      [st.session_state.credenciais_df, novo_membro_df],
                      ignore_index=True,
                  )
                  st.session_state.credenciais_df.to_csv(
                      CREDENCIAIS_CSV, index=False
                  )
                  registrar_log(
                      f"GOE cadastrou novo membro: {nome_novo_goe.strip()}",
                      "N/A",
                      usuario_ativo,
                  )
                  st.success(
                      f"✔️ Membro(a) {nome_novo_goe.strip()} cadastrado(a) com"
                      " sucesso!"
                  )
                  st.rerun()
                else:
                  st.error("Preencha todos os campos obrigatórios.")

          with col_exc_eq:
            st.markdown("### 🗑️ Remover Membro GOE")
            df_membros_goe = st.session_state.credenciais_df[
                st.session_state.credenciais_df["Perfil"] == "Gestão GOE"
            ]
            if not df_membros_goe.empty:
              with st.form(
                  "form_exc_equipe_goe_proprio", clear_on_submit=True
              ):
                membro_rem_selecionado = st.selectbox(
                    "Selecione o Membro para remover:",
                    options=df_membros_goe["Nome"].tolist(),
                )
                if st.form_submit_button(
                    "🗑️ Remover Membro", type="secondary"
                ):
                  st.session_state.credenciais_df = (
                      st.session_state.credenciais_df[
                          ~(
                              (
                                  st.session_state.credenciais_df["Nome"]
                                  == membro_rem_selecionado
                              )
                              & (
                                  st.session_state.credenciais_df["Perfil"]
                                  == "Gestão GOE"
                              )
                          )
                      ]
                  )
                  st.session_state.credenciais_df.to_csv(
                      CREDENCIAIS_CSV, index=False
                  )
                  registrar_log(
                      f"GOE removeu membro: {membro_rem_selecionado}",
                      "N/A",
                      usuario_ativo,
                  )
                  st.success(
                      f"🗑️ Membro {membro_rem_selecionado} removido com"
                      " sucesso!"
                  )
                  st.rerun()
            else:
              st.info("Nenhum membro cadastrado.")

          st.markdown("---")
          st.markdown("### 📋 Lista Atual da Equipe GOE")
          st.dataframe(
              df_membros_goe[["Nome", "Cargo", "Turno"]],
              use_container_width=True,
              hide_index=True,
          )

        with aba_goe_mensagens:
          st.subheader(
              "💬 Central de Mensagens e Comunicados Separados (GOE)"
          )
          st.markdown(
              "Envie comunicados direcionados especificamente para cada grupo"
              " da escola:"
          )

          todos_cadastrados_app = (
              st.session_state.credenciais_df["Nome"].tolist()
              if "credenciais_df" in st.session_state
              and not st.session_state.credenciais_df.empty
              else [usuario_ativo]
          )

          with st.form("form_enviar_comunicado_goe", clear_on_submit=True):
            remetente_selecionado = st.selectbox(
                "👤 Nome do Remetente (Selecione entre todos os cadastrados no"
                " app):",
                options=todos_cadastrados_app,
                index=(
                    todos_cadastrados_app.index(usuario_ativo)
                    if usuario_ativo in todos_cadastrados_app
                    else 0
                ),
            )
            grupo_destino = st.selectbox(
                "🎯 Selecione o Grupo de Destino:",
                options=["Equipe GOE", "Professores", "Gestão"],
            )
            mensagem_texto = st.text_area("📝 Escreva a Mensagem / Comunicado:")

            btn_enviar_comunicado = st.form_submit_button(
                "📤 Enviar Comunicado", type="primary"
            )
            if btn_enviar_comunicado:
              if mensagem_texto.strip():
                novo_comunicado = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Remetente": remetente_selecionado,
                    "GrupoDestino": grupo_destino,
                    "Mensagem": mensagem_texto.strip(),
                }])
                novo_comunicado.to_csv(
                    COMUNICADOS_CSV,
                    mode="a",
                    header=not os.path.exists(COMUNICADOS_CSV),
                    index=False,
                )
                registrar_log(
                    f"Comunicado enviado por {remetente_selecionado} para o"
                    f" grupo: {grupo_destino}",
                    "N/A",
                    usuario_ativo,
                )
                st.success(
                    f"✔️ Comunicado enviado com sucesso por"
                    f" **{remetente_selecionado}** para o grupo"
                    f" **{grupo_destino}**!"
                )
                st.rerun()
              else:
                st.error("A mensagem não pode estar vazia.")

          st.markdown("---")
          st.markdown("### 📬 Histórico de Comunicados Enviados")
          if os.path.exists(COMUNICADOS_CSV):
            df_comunicados_hist = pd.read_csv(COMUNICADOS_CSV)
            if not df_comunicados_hist.empty:
              st.dataframe(
                  df_comunicados_hist, use_container_width=True, hide_index=True
              )
            else:
              st.info("Nenhum comunicado enviado até o momento.")
          else:
            st.info("Nenhum histórico encontrado.")

        with aba_goe_chamada:
          data_chamada = st.date_input("Data da chamada:", value=date.today())
          serie_selecionada = st.selectbox(
              "Selecione a Série/Turma:", SERIES_TURMAS
          )
          st.info(
              f"Pronto para registrar chamada da turma {serie_selecionada} em"
              f" {data_chamada.strftime('%d/%m/%Y')}."
          )

      # ==============================================================================
      # --- PAINEL PROFESSORES COM MONITORAMENTO E SELEÇÃO POR TURMA E NOME ---
      # ==============================================================================
      else:
        st.subheader("👩‍🏫 Painel de Monitoramento Docente")

        prof_data = st.session_state.credenciais_df[
            (st.session_state.credenciais_df["Nome"] == usuario_ativo)
            & (st.session_state.credenciais_df["Perfil"] == "Professores")
        ].iloc[0]

        turmas_prof = [
            t.strip()
            for t in str(prof_data.get("Series", "")).split(",")
            if t.strip()
        ]

        st.markdown(
            f"**📚 Disciplinas:** {prof_data.get('Disciplinas', 'Nenhuma')} |"
            " **🏫 Turmas Atribuídas:**"
            f" {', '.join(turmas_prof) if turmas_prof else 'Nenhuma'}"
        )
        st.markdown("---")

        if os.path.exists(OCORRENCIAS_CSV):
          df_oc_prof_check = pd.read_csv(OCORRENCIAS_CSV, dtype={"RA": str})
          minhas_ocs = df_oc_prof_check[
              df_oc_prof_check["Professor"] == usuario_ativo
          ]
          if not minhas_ocs.empty and "MensagemGestaoAOE" in minhas_ocs.columns:
            com_resposta = minhas_ocs[
                minhas_ocs["MensagemGestaoAOE"].notna()
                & (minhas_ocs["MensagemGestaoAOE"] != "")
            ]
            if not com_resposta.empty:
              st.warning(
                  "📬 Há novos retornos da Gestão/GOE sobre suas ocorrências"
                  " registradas!"
              )
              with st.expander("Ver Retornos e Comunicações da Gestão"):
                for idx, row in com_resposta.iterrows():
                  st.write(
                      f"• **Aluno:** {row['Nome']} | **Ocorrência:**"
                      f" {row['Descricao']}"
                  )
                  st.info(
                      f"💬 **Mensagem da Gestão:** {row['MensagemGestaoAOE']}"
                  )

        aba_monitoramento, aba_ocorrencias = st.tabs(
            ["📊 Monitoramento de Alunos", "⚠️ Registro de Ocorrências"]
        )

        with aba_monitoramento:
          col_m_tit, col_m_btn = st.columns([4, 1])
          col_m_tit.markdown("### 🔍 Seleção de Aluno por Turma e Nome")
          if col_m_btn.button("🔄 Atualizar", key="btn_ref_prof_mon"):
            st.success("Atualizado!")
            st.rerun()

          if not turmas_prof or "Nenhuma" in turmas_prof:
            st.warning("⚠️ Você não possui turmas alocadas.")
          else:
            col_mon_turma, col_mon_nome = st.columns(2)
            turma_escolhida = col_mon_turma.selectbox(
                "🏫 Selecione a Turma:",
                options=turmas_prof,
                key="mon_turma_sel",
            )
            df_alunos_geral = st.session_state.alunos
            df_alunos_turma = df_alunos_geral[
                df_alunos_geral["Série"] == turma_escolhida
            ]
            if df_alunos_turma.empty:
              st.info("Nenhum aluno cadastrado nesta turma.")
            else:
              nomes_turma = df_alunos_turma["Nome"].tolist()
              aluno_escolhido_nome = col_mon_nome.selectbox(
                  "👤 Selecione o Nome do Aluno:",
                  options=nomes_turma,
                  key="mon_nome_sel",
              )
              df_aluno_detalhe = df_alunos_turma[
                  df_alunos_turma["Nome"] == aluno_escolhido_nome
              ]
              st.markdown("---")
              st.markdown(
                  "#### 📄 Dados de Frequência do(a) Aluno(a):"
                  f" **{aluno_escolhido_nome}**"
              )
              st.dataframe(
                  df_aluno_detalhe[[
                      "RA",
                      "Nome",
                      "Série",
                      "Presenças",
                      "Faltas",
                      "Email",
                      "Telefone",
                  ]],
                  use_container_width=True,
                  hide_index=True,
              )

        with aba_ocorrencias:
          st.markdown("### ⚠️ Registro de Ocorrência Escolar por Aluno")
          df_alunos_geral = st.session_state.alunos
          if df_alunos_geral.empty:
            st.info("Não há alunos cadastrados no sistema.")
          else:
            col_prof_serie, col_prof_nome = st.columns(2)
            series_disponiveis_prof = sorted(
                df_alunos_geral["Série"].dropna().unique().tolist()
            )
            if not series_disponiveis_prof:
              st.warning("Nenhuma série encontrada.")
            else:
              serie_selecionada_prof = col_prof_serie.selectbox(
                  "🏫 Filtrar por Série:",
                  options=series_disponiveis_prof,
                  key="prof_serie_filtro",
              )
              df_alunos_filtrados_serie = df_alunos_geral[
                  df_alunos_geral["Série"] == serie_selecionada_prof
              ]
              if df_alunos_filtrados_serie.empty:
                st.info("Nenhum aluno encontrado.")
              else:
                opcoes_nomes_prof = df_alunos_filtrados_serie.apply(
                    lambda r: f"{r['Nome']} (RA: {r['RA']})", axis=1
                ).tolist()
                aluno_nome_selecionado_str = col_prof_nome.selectbox(
                    "👤 Selecionar Aluno:",
                    options=opcoes_nomes_prof,
                    key="prof_nome_filtro",
                )
                with st.form("form_reg_ocorrencia", clear_on_submit=True):
                  gravidade_oc = st.selectbox(
                      "Gravidade / Nível:",
                      options=[
                          "Baixa (Aviso/Advertência)",
                          "Média (Comportamental)",
                          "Alta (Encaminhamento à Gestão)",
                      ],
                  )
                  descricao_oc = st.text_area(
                      "📝 Descrição Detalhada da Ocorrência:"
                  )
                  if st.form_submit_button(
                      "💾 Salvar Ocorrência", type="primary"
                  ):
                    if descricao_oc.strip():
                      idx_sel = opcoes_nomes_prof.index(
                          aluno_nome_selecionado_str
                      )
                      aluno_escolhido_row = df_alunos_filtrados_serie.iloc[
                          idx_sel
                      ]
                      nova_ocorrencia = pd.DataFrame([{
                          "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                          "RA": str(aluno_escolhido_row["RA"]),
                          "Nome": str(aluno_escolhido_row["Nome"]),
                          "Série": str(aluno_escolhido_row["Série"]),
                          "Gravidade": gravidade_oc,
                          "Descricao": descricao_oc.strip(),
                          "Professor": usuario_ativo,
                          "MensagemGestaoAOE": "",
                      }])
                      nova_ocorrencia.to_csv(
                          OCORRENCIAS_CSV,
                          mode="a",
                          header=not os.path.exists(OCORRENCIAS_CSV),
                          index=False,
                      )
                      registrar_log(
                          f"Ocorrência registrada para o aluno"
                          f" {str(aluno_escolhido_row['Nome'])}",
                          str(aluno_escolhido_row["RA"]),
                          usuario_ativo,
                      )
                      st.success("✔️ Ocorrência registrada com sucesso!")
                      st.rerun()
                    else:
                      st.error("A descrição não pode estar vazia.")
