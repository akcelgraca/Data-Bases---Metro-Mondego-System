-- 06_refresh_report_dates.sql

-- 1. Preencher linha_id para os bilhetes que não tenham (necessário para relatórios de linha)
-- Escolhemos a linha 1 como default se for NULL
UPDATE bilhete SET linha_id = 1 WHERE linha_id IS NULL;

-- 2. Atualizar a data de compra para os últimos 30 dias (garantir relatórios ativos)
UPDATE bilhete SET data_compra = CURRENT_DATE - (RANDOM() * 15 * INTERVAL '1 day') WHERE data_compra < CURRENT_DATE - INTERVAL '30 days';

-- 3. Atualizar carimbos na validacao que possam estar desatualizados
UPDATE validacao SET data_hora = CURRENT_TIMESTAMP - (RANDOM() * 5 * INTERVAL '1 day') WHERE data_hora < CURRENT_TIMESTAMP - INTERVAL '30 days';