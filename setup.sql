-- ========================================
-- TABELA: MEETINGS
-- ========================================
CREATE TABLE IF NOT EXISTS ameetings (
    meeting_id STRING,
    titulo STRING,
    horario TIMESTAMP,
    meet_link STRING,

    -- CONTROLE DE ACESSO
    hash_link STRING,

    -- CONTEXTO DO GRUPO
    grupo STRING,
    tipo_grupo STRING,

    -- CONTROLE DE LINK
    ativo BOOLEAN DEFAULT true,
    expira_em TIMESTAMP,

    -- METADATA
    created_at TIMESTAMP DEFAULT current_timestamp()
);

-- ========================================
-- TABELA: RESPOSTAS (CHECK-IN)
-- ========================================
CREATE TABLE IF NOT EXISTS meet_respostas (
    meeting_id STRING,
    nome STRING,
    email STRING,
    cpf STRING,
    data_resposta TIMESTAMP
);

-- ========================================
-- TABELA: VIEW DE PRESENÇA (base analítica)
-- ========================================
CREATE OR REPLACE VIEW vw_presenca AS
SELECT 
    m.meeting_id,
    m.titulo,
    m.grupo,
    m.tipo_grupo,
    m.horario,

    r.nome,
    r.email,
    r.cpf,
    r.data_resposta,

    -- atraso em minutos
    ROUND(
        (unix_timestamp(r.data_resposta) - unix_timestamp(m.horario)) / 60
    ) AS atraso_minutos,

    -- flag presença válida (dentro da janela)
    CASE 
        WHEN r.data_resposta BETWEEN 
            m.horario - INTERVAL 5 MINUTES AND 
            m.horario + INTERVAL 1 HOUR
        THEN 1 ELSE 0
    END AS presenca_valida

FROM meet_respostas r
JOIN meetings m
    ON r.meeting_id = m.meeting_id;

-- ========================================
-- TABELA: VIEW DE INDICADORES POR REUNIÃO
-- ========================================
CREATE OR REPLACE VIEW indicadores_reuniao AS
SELECT 
    meeting_id,
    titulo,
    grupo,
    tipo_grupo,

    COUNT(*) AS total_checkins,

    COUNT(DISTINCT cpf) AS participantes_unicos,

    SUM(presenca_valida) AS presencas_validas,

    ROUND(AVG(atraso_minutos), 1) AS atraso_medio_min,

    MIN(data_resposta) AS primeiro_checkin,
    MAX(data_resposta) AS ultimo_checkin

FROM vw_presenca
GROUP BY 
    meeting_id,
    titulo,
    grupo,
    tipo_grupo;

-- ========================================
-- TABELA: VIEW DE INDICADORES POR REUNIÃO
-- ========================================

CREATE OR REPLACE VIEW indicadores_gerais AS
SELECT 

    COUNT(DISTINCT meeting_id) AS total_reunioes,

    COUNT(*) AS total_checkins,

    COUNT(DISTINCT cpf) AS total_participantes,

    ROUND(AVG(atraso_minutos), 1) AS atraso_medio_geral,

    ROUND(
        SUM(presenca_valida) * 100.0 / COUNT(*),
        1
    ) AS taxa_presenca_valida_pct

FROM vw_presenca;

-- ========================================
-- TABELA: VIEW DE DUPLICIDADE (controle)
-- ========================================

CREATE OR REPLACE VIEW vw_duplicidade AS
SELECT 
    meeting_id,
    cpf,
    COUNT(*) AS qtd
FROM meet_respostas
GROUP BY meeting_id, cpf
HAVING COUNT(*) > 1;
