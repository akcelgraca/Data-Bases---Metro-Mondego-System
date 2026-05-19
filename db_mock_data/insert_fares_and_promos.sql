-- 03_insert_fares_and_promos.sql

-- 1. TIPO_BILHETE
INSERT INTO tipo_bilhete (id_tipo, nome) VALUES
(1, 'single_trip'),
(2, 'daily'),
(3, 'monthly_pass'),
(4, 'monthly_student'),
(5, 'monthly_senior');

-- 2. HISTORICO_PRECO
INSERT INTO historico_preco (preco, data_efetiva, tipo_bilhete_id_tipo) VALUES
(1.50, CURRENT_DATE - INTERVAL '1 year', 1),
(4.00, CURRENT_DATE - INTERVAL '1 year', 2),
(30.00, CURRENT_DATE - INTERVAL '1 year', 3),
(20.00, CURRENT_DATE - INTERVAL '1 year', 4),
(15.00, CURRENT_DATE - INTERVAL '1 year', 5),
(1.75, CURRENT_DATE + INTERVAL '1 month', 1);   -- aumento futuro para single_trip

-- 3. PROMOCAO
INSERT INTO promocao (id_promocao, nome, desconto, data_inicio, data_fim, tipo_bilhete_id_tipo, linha_id) VALUES
(1, 'School Holidays', 20, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '20 days', 2, 1),
(2, 'Summer Sale', 10, CURRENT_DATE + INTERVAL '1 month', CURRENT_DATE + INTERVAL '2 months', 1, 3);

-- Atualizar sequência
SELECT setval(pg_get_serial_sequence('promocao', 'id_promocao'), COALESCE((SELECT MAX(id_promocao) FROM promocao), 1), TRUE);
