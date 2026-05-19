-- 05_insert_tickets_and_validations.sql

-- 1. AVISO
INSERT INTO aviso (id, titulo, mensagem, data_emissao, administrador_pessoa_id) VALUES
(1, 'Strike Notice', 'Possible delays between 10:00 and 13:00', CURRENT_DATE - INTERVAL '1 day', 2),
(2, 'Maintenance', 'Line 2 closed on weekend', CURRENT_DATE - INTERVAL '2 days', 1);

-- 2. CARREGAMENTO
INSERT INTO carregamento (id_carregamento, valor, metodo_pagamento, data_hora, cliente_pessoa_id) VALUES
(1, 50.00, 'card', CURRENT_TIMESTAMP - INTERVAL '1 day', 3),
(2, 20.00, 'multibanco', CURRENT_TIMESTAMP - INTERVAL '1 day 2 hours', 4),
(3, 100.00, 'card', CURRENT_TIMESTAMP - INTERVAL '2 days', 5),
(4, 30.00, 'card', CURRENT_TIMESTAMP - INTERVAL '3 hours', 6);

-- 3. BILHETE
INSERT INTO bilhete (id, data_compra, preco_compra, data_inicio_validade, data_fim_validade, data_viagem, data_expiracao, estado, metodo_pagamento, desconto_aplicado, tipo_bilhete_id_tipo, cliente_pessoa_id, linha_id) VALUES
(1001, CURRENT_DATE, 1.50, NULL, NULL, CURRENT_DATE, NULL, 'ativo', 'wallet', 0, 1, 3, 1),
(1002, CURRENT_DATE, 4.00, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day', NULL, NULL, 'ativo', 'wallet', 0, 2, 4, 1),
(1003, CURRENT_DATE - INTERVAL '1 day', 30.00, CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE + INTERVAL '29 days', NULL, NULL, 'ativo', 'wallet', 0, 3, 5, 3),
(1004, CURRENT_DATE, 1.50, NULL, NULL, CURRENT_DATE, NULL, 'ativo', 'wallet', 0, 1, 6, 1),
(1005, CURRENT_DATE, 20.00, CURRENT_DATE, CURRENT_DATE + INTERVAL '30 days', NULL, NULL, 'ativo', 'card', 0, 4, 7, 2);

-- 4. VALIDACAO
-- Assume ids inseridos manualmente
INSERT INTO validacao (data_hora, bilhete_id, viagem_id, paragem_id) VALUES
(CURRENT_DATE + TIME '08:12:00', 1001, 101, 1),
(CURRENT_DATE + TIME '08:00:00', 1002, 201, 1),
(CURRENT_DATE + TIME '10:30:00', 1002, 202, 3),
(CURRENT_DATE + TIME '08:00:00' - INTERVAL '1 day', 1003, 301, 6),
(CURRENT_DATE + TIME '18:00:00' - INTERVAL '1 day', 1003, 303, 1),
(CURRENT_DATE + TIME '07:15:00', 1003, 302, 6);

-- 5. AVISO_CLIENTE
INSERT INTO aviso_cliente (data_entrega, data_leitura, lido, aviso_id, cliente_pessoa_id) VALUES
(CURRENT_DATE - INTERVAL '1 day', NULL, FALSE, 1, 3),
(CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE - INTERVAL '1 day', TRUE, 1, 4),
(CURRENT_DATE - INTERVAL '2 days', NULL, FALSE, 2, 5);

-- 6. INTERRUPCAO_LINHA
INSERT INTO interrupcao_linha (id_interrupcao, data_inicio, data_fim, motivo, estado, administrador_pessoa_id, linha_id) VALUES
(1, CURRENT_DATE + INTERVAL '5 days', CURRENT_DATE + INTERVAL '6 days', 'Manutenção da via', TRUE, 2, 1),
(2, CURRENT_DATE + INTERVAL '10 days', CURRENT_DATE + INTERVAL '10 days', 'Evento cultural', FALSE, 1, 2);

-- Atualizar sequências
SELECT setval(pg_get_serial_sequence('bilhete', 'id'), COALESCE((SELECT MAX(id) FROM bilhete), 1), TRUE);
SELECT setval(pg_get_serial_sequence('aviso', 'id'), COALESCE((SELECT MAX(id) FROM aviso), 1), TRUE);
SELECT setval(pg_get_serial_sequence('carregamento', 'id_carregamento'), COALESCE((SELECT MAX(id_carregamento) FROM carregamento), 1), TRUE);
