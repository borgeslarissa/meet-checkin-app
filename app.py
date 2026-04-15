import streamlit as st
from databricks import sql
import os
import re
from datetime import datetime, timedelta

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Check-in da reunião")

st.title("Antes de entrar na reunião")

# -------------------------
# DATABRICKS (via secrets)
# -------------------------
SERVER_HOSTNAME = os.environ["DATABRICKS_HOST"]
HTTP_PATH = os.environ["DATABRICKS_HTTP_PATH"]
ACCESS_TOKEN = os.environ["DATABRICKS_TOKEN"]

# -------------------------
# PEGAR PARAM
# -------------------------
params = st.query_params
meeting_id = params.get("meeting_id")

if isinstance(meeting_id, list):
    meeting_id = meeting_id[0]

if not meeting_id:
    st.error("Link inválido")
    st.stop()

# -------------------------
# FUNÇÕES SQL
# -------------------------
def run_query(query):
    with sql.connect(
        server_hostname=SERVER_HOSTNAME,
        http_path=HTTP_PATH,
        access_token=ACCESS_TOKEN,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return rows, columns

def run_insert(query):
    with sql.connect(
        server_hostname=SERVER_HOSTNAME,
        http_path=HTTP_PATH,
        access_token=ACCESS_TOKEN,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)

# -------------------------
# BUSCAR REUNIÃO
# -------------------------
query = f"""
SELECT meet_link, titulo, horario
FROM hsl_prod.bronzev2.apost_meetings
WHERE meeting_id = '{meeting_id}'
"""

rows, columns = run_query(query)

if not rows:
    st.error("Reunião não encontrada")
    st.stop()

row_dict = dict(zip(columns, rows[0]))

meet_link = str(row_dict["meet_link"]).strip()
titulo = row_dict["titulo"]
horario = row_dict["horario"]

# -------------------------
# INFO
# -------------------------
st.subheader(f"Reunião: {titulo}")
st.caption(f"Horário: {horario}")

# -------------------------
# ⏰ CONTROLE DE HORÁRIO
# -------------------------
horario_dt = datetime.fromisoformat(horario.replace("Z", ""))
agora = datetime.utcnow()

inicio = horario_dt - timedelta(minutes=5)
fim = horario_dt + timedelta(hours=1)

if agora < inicio:
    st.error("⏳ Essa reunião ainda não começou.")
    st.stop()

if agora > fim:
    st.error("❌ O acesso já foi encerrado.")
    st.stop()

# -------------------------
# VALIDAR CPF
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

st.caption("Seus dados são usados apenas para identificação.")

# -------------------------
# SALVAR
# -------------------------
if st.button("Entrar na reunião"):

    if not nome or not email or not cpf:
        st.warning("Preencha todos os campos")
        st.stop()

    if not validar_cpf(cpf):
        st.warning("CPF inválido")
        st.stop()

    insert = f"""
    INSERT INTO hsl_prod.bronzev2.apost_meet_respostas
    VALUES (
        '{meeting_id}',
        '{nome}',
        '{email}',
        '{cpf}',
        current_timestamp()
    )
    """

    with st.spinner("Entrando..."):
        run_insert(insert)

    st.success("Redirecionando...")

    st.markdown(
        f'<meta http-equiv="refresh" content="2;url={meet_link}">',
        unsafe_allow_html=True
    )
