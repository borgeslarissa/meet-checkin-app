import streamlit as st
from databricks.sdk import WorkspaceClient
from datetime import datetime, timedelta
import re

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Check-in da reunião")

st.title("Antes de entrar na reunião")
st.write("Preencha seus dados para continuar")

# -------------------------
# CLIENTE DATABRICKS
# -------------------------
w = WorkspaceClient()
WAREHOUSE_ID = "seu_id"

# -------------------------
# FUNÇÕES SQL
# -------------------------
def run_query(query):
    result = w.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID,
        statement=query,
        wait_timeout="10s"
    )

    if not result.result or not result.result.data_array:
        return []

    return result.result.data_array


def run_insert(query):
    w.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID,
        statement=query,
        wait_timeout="10s"
    )

# -------------------------
# PEGAR TOKEN
# -------------------------
params = st.query_params
token = params.get("token")

if isinstance(token, list):
    token = token[0]

if not token:
    st.error("Link inválido")
    st.stop()

# -------------------------
# BUSCAR REUNIÃO
# -------------------------
query = f"""
SELECT 
    meeting_id,
    titulo,
    horario,
    meet_link,
    ativo,
    expira_em
FROM meetings
WHERE hash_link = '{token}'
"""

rows = run_query(query)

if not rows:
    st.error("Reunião não encontrada")
    st.stop()

row = rows[0]

meeting_id = row[0]
titulo = row[1]
horario = row[2]
meet_link = str(row[3]).strip()
ativo = row[4]
expira_em = row[5]

# -------------------------
# VALIDAÇÕES DE ACESSO
# -------------------------
if not ativo:
    st.error("🚫 Este link foi desativado.")
    st.stop()

agora = datetime.utcnow()

# expiração
if expira_em:
    expira_dt = datetime.fromisoformat(str(expira_em).replace("Z", ""))
    if agora > expira_dt:
        st.error("⏰ Este link expirou.")
        st.stop()

# controle de horário
horario_dt = datetime.fromisoformat(str(horario).replace("Z", ""))

inicio = horario_dt - timedelta(minutes=5)
fim = horario_dt + timedelta(hours=1)

if agora < inicio:
    st.error("⏳ Essa reunião ainda não começou.")
    st.stop()

if agora > fim:
    st.error("❌ O acesso a essa reunião já foi encerrado.")
    st.stop()

# -------------------------
# INFO
# -------------------------
st.subheader(f"Reunião: {titulo}")
st.caption(f"Horário: {horario_dt.strftime('%d/%m %H:%M')}")

# -------------------------
# VALIDAÇÃO CPF
# -------------------------
def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    return len(cpf) == 11

# -------------------------
# FORMULÁRIO
# -------------------------
nome = st.text_input("Nome completo")
email = st.text_input("Email")
cpf = st.text_input("CPF")

st.caption("Seus dados são usados apenas para identificação na reunião.")

# -------------------------
# SALVAR + REDIRECIONAR
# -------------------------
if st.button("Entrar na reunião"):

    # 🔁 valida horário novamente (segurança)
    agora = datetime.utcnow()

    if agora < inicio:
        st.error("⏳ A reunião ainda não começou.")
        st.stop()

    if agora > fim:
        st.error("❌ O acesso à reunião foi encerrado.")
        st.stop()

    if not nome or not email or not cpf:
        st.warning("Preencha todos os campos")
        st.stop()

    if not validar_cpf(cpf):
        st.warning("CPF inválido")
        st.stop()

    insert = f"""
    INSERT INTO meet_respostas
    VALUES (
        '{meeting_id}',
        '{nome}',
        '{email}',
        '{cpf}',
        current_timestamp()
    )
    """

    with st.spinner("Entrando na reunião..."):
        run_insert(insert)

    st.success("Tudo certo! Redirecionando...")

    st.markdown(
        f'<meta http-equiv="refresh" content="2;url={meet_link}">',
        unsafe_allow_html=True
    )
