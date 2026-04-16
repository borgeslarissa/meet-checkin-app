# Runbook - Meeting Check-in

## Criar nova reunião

INSERT INTO meetings (...)

---

## Gerar link de acesso

SELECT 
    CONCAT('<app-url>?token=', hash_link)
FROM meetings

---

## Desativar link

UPDATE meetings
SET ativo = false
WHERE meeting_id = 'ID'

---

## Expirar reunião

UPDATE meetings
SET expira_em = current_timestamp()
WHERE meeting_id = 'ID'

---

## Consultar presença

SELECT *
FROM vw_lista_presenca

---

## Ver duplicidade

SELECT cpf, COUNT(*)
FROM meet_respostas
GROUP BY cpf
HAVING COUNT(*) > 1
