-- 1. Preencher linha_id para os bilhetes antigos (escolhe uma linha à tua escolha)
UPDATE bilhete SET linha_id = 1 WHERE linha_id IS NULL;

-- 2. Atualizar a data de compra para os últimos 30 dias (ex.: hoje)
UPDATE bilhete SET data_compra = CURRENT_DATE WHERE data_compra < CURRENT_DATE - INTERVAL '30 days';