-- ============================================================
-- INSERÇÃO DE DADOS PARA O PROJETO METRO MONDEGO
-- Ordem respeita dependências de chaves estrangeiras
-- ============================================================

-- 1. PESSOA, CLIENTE e ADMINISTRADOR
INSERT INTO pessoa (id, nome, email, username, password_hash) VALUES
(1, 'Super Admin', 'super@metromondego.pt', 'superadmin', 'hash_super'),
(2, 'Admin Operações', 'admin1@metromondego.pt', 'admin1', 'hash_admin1'),
(3, 'Ana Costa', 'ana.costa@email.pt', 'anacosta', 'hash_ana'),
(4, 'Bruno Silva', 'bruno.s@email.pt', 'brunosilva', 'hash_bruno'),
(5, 'Carla Mendes', 'carla.m@email.pt', 'carlam', 'hash_carla'),
(6, 'Diogo Santos', 'diogo.s@email.pt', 'diogos', 'hash_diogo'),
(7, 'Elisa Pereira', 'elisa.p@email.pt', 'elisap', 'hash_elisa');

INSERT INTO cliente (wallet, nif, telefone, pessoa_id) VALUES
(50.00, '123456789', '910000001', 3),
(20.00, '234567890', '910000002', 4),
(100.00, '345678901', '910000003', 5),
(5.00, '456789012', '910000004', 6),
(75.50, '567890123', '910000005', 7);

INSERT INTO administrador (is_super, pessoa_id) VALUES
(TRUE, 1),
(FALSE, 2);

-- 2. LINHA (3 linhas fixas)
INSERT INTO linha (id, nome, hora_inicio, hora_fim, frequencia, capacidade_default) VALUES
(1, 'Portagem - Hospital', '07:30:00', '21:00:00', 20, 50),
(2, 'Portagem - Estacao B', '07:45:00', '19:00:00', 30, 50),
(3, 'Portagem - Miranda do Corvo - Lousa', '07:00:00', '19:00:00', 90, 50);

-- 3. PARAGEM
INSERT INTO paragem (id, nome) VALUES
(1, 'Portagem'),
(2, 'Hospital'),
(3, 'Estacao B'),
(4, 'Miranda do Corvo'),
(5, 'Lousa'),
(6, 'Serpins');

-- 4. TRAJETO (ordem das paragens por linha)
-- Linha 1: Portagem -> Hospital (ida)
INSERT INTO trajeto (sequencia, tempo_previsto_desde_origem, distancia_acumulada, plataforma_sentido, linha_id, paragem_id) VALUES
(1, 0, 0.0, 'A', 1, 1),
(2, 15, 8.5, 'A', 1, 2);
-- Linha 1 (volta): Hospital -> Portagem (direção oposta)
INSERT INTO trajeto (sequencia, tempo_previsto_desde_origem, distancia_acumulada, plataforma_sentido, linha_id, paragem_id) VALUES
(1, 0, 0.0, 'B', 1, 2),
(2, 15, 8.5, 'B', 1, 1);

-- Linha 2: Portagem -> Estacao B (ida)
INSERT INTO trajeto (sequencia, tempo_previsto_desde_origem, distancia_acumulada, plataforma_sentido, linha_id, paragem_id) VALUES
(1, 0, 0.0, 'A', 2, 1),
(2, 12, 6.2, 'A', 2, 3);
-- Linha 2 (volta): Estacao B -> Portagem
INSERT INTO trajeto (sequencia, tempo_previsto_desde_origem, distancia_acumulada, plataforma_sentido, linha_id, paragem_id) VALUES
(1, 0, 0.0, 'B', 2, 3),
(2, 12, 6.2, 'B', 2, 1);

-- Linha 3: Serpins -> Portagem (ida)
INSERT INTO trajeto (sequencia, tempo_previsto_desde_origem, distancia_acumulada, plataforma_sentido, linha_id, paragem_id) VALUES
(1, 0, 0.0, 'A', 3, 6),
(2, 20, 12.0, 'A', 3, 4),
(3, 35, 22.5, 'A', 3, 5),
(4, 60, 35.0, 'A', 3, 1);
-- Linha 3 (volta): Portagem -> Serpins
INSERT INTO trajeto (sequencia, tempo_previsto_desde_origem, distancia_acumulada, plataforma_sentido, linha_id, paragem_id) VALUES
(1, 0, 0.0, 'B', 3, 1),
(2, 25, 12.5, 'B', 3, 5),
(3, 40, 22.5, 'B', 3, 4),
(4, 60, 35.0, 'B', 3, 6);

-- 5. TIPO_BILHETE
INSERT INTO tipo_bilhete (id_tipo, nome) VALUES
(1, 'single_trip'),
(2, 'daily'),
(3, 'monthly_pass'),
(4, 'monthly_student'),
(5, 'monthly_senior');

-- 6. HISTORICO_PRECO (preços atuais e anteriores)
INSERT INTO historico_preco (preco, data_efetiva, tipo_bilhete_id_tipo) VALUES
(1.50, '2025-01-01', 1),
(4.00, '2025-01-01', 2),
(30.00, '2025-01-01', 3),
(20.00, '2025-01-01', 4),
(15.00, '2025-01-01', 5),
(1.75, '2025-06-01', 1);   -- aumento futuro para single_trip

-- 7. VIAGEM (baseadas nos horários das linhas, datas recentes)
-- Linha 1, direção 'ida' (Portagem->Hospital)
INSERT INTO viagem (id, data_hora_partida, direcao, capacidade_disponivel, atraso_estimado, linha_id) VALUES
(101, '2025-04-10 08:10:00', 'ida', 50, 0, 1),
(102, '2025-04-10 08:30:00', 'ida', 48, 2, 1),
(103, '2025-04-10 08:50:00', 'ida', 50, 0, 1);
-- Linha 1, direção 'volta'
INSERT INTO viagem (id, data_hora_partida, direcao, capacidade_disponivel, atraso_estimado, linha_id) VALUES
(104, '2025-04-10 08:20:00', 'volta', 50, 0, 1),
(105, '2025-04-10 08:40:00', 'volta', 50, 0, 1);

-- Linha 2
INSERT INTO viagem (id, data_hora_partida, direcao, capacidade_disponivel, atraso_estimado, linha_id) VALUES
(201, '2025-04-10 07:45:00', 'ida', 45, 0, 2),
(202, '2025-04-10 08:15:00', 'ida', 50, 0, 2),
(203, '2025-04-10 07:50:00', 'volta', 50, 0, 2);

-- Linha 3
INSERT INTO viagem (id, data_hora_partida, direcao, capacidade_disponivel, atraso_estimado, linha_id) VALUES
(301, '2025-04-10 07:00:00', 'ida', 50, 0, 3),
(302, '2025-04-10 08:30:00', 'ida', 50, 0, 3),
(303, '2025-04-10 08:00:00', 'volta', 50, 0, 3),
(304, '2025-04-10 09:30:00', 'volta', 50, 0, 3);

-- 8. PROMOCAO
INSERT INTO promocao (id_promocao, nome, desconto, data_inicio, data_fim, tipo_bilhete_id_tipo, linha_id) VALUES
(1, 'School Holidays', 20, '2025-07-01', '2025-07-31', 2, 1),
(2, 'Summer Sale', 10, '2025-08-01', '2025-08-15', 1, 3);

-- 9. CARREGAMENTO (top‑ups de wallet)
INSERT INTO carregamento (id_carregamento, valor, metodo_pagamento, data_hora, cliente_pessoa_id) VALUES
(1, 50.00, 'card', '2025-04-09 10:30:00', 3),
(2, 20.00, 'multibanco', '2025-04-09 14:20:00', 4),
(3, 100.00, 'card', '2025-04-08 09:15:00', 5),
(4, 30.00, 'card', '2025-04-10 08:05:00', 6);

-- 10. BILHETE (compras realizadas)
-- Cliente 3 compra single_trip para linha 1
INSERT INTO bilhete (id, data_compra, preco_compra, data_inicio_validade, data_fim_validade, data_viagem, data_expiracao, estado, metodo_pagamento, desconto_aplicado, tipo_bilhete_id_tipo, cliente_pessoa_id) VALUES
(1001, '2025-04-10', 1.50, NULL, NULL, '2025-04-10', NULL, 'ativo', 'wallet', 0, 1, 3);
-- Cliente 4 compra daily para linha 2
INSERT INTO bilhete (id, data_compra, preco_compra, data_inicio_validade, data_fim_validade, data_viagem, data_expiracao, estado, metodo_pagamento, desconto_aplicado, tipo_bilhete_id_tipo, cliente_pessoa_id) VALUES
(1002, '2025-04-10', 4.00, '2025-04-10', '2025-04-11', NULL, NULL, 'ativo', 'wallet', 0, 2, 4);
-- Cliente 5 compra monthly_pass para linha 3
INSERT INTO bilhete (id, data_compra, preco_compra, data_inicio_validade, data_fim_validade, data_viagem, data_expiracao, estado, metodo_pagamento, desconto_aplicado, tipo_bilhete_id_tipo, cliente_pessoa_id) VALUES
(1003, '2025-04-09', 30.00, '2025-04-09', '2025-05-09', NULL, NULL, 'ativo', 'wallet', 0, 3, 5);
-- Cliente 6 compra single_trip (será usado para validação)
INSERT INTO bilhete (id, data_compra, preco_compra, data_inicio_validade, data_fim_validade, data_viagem, data_expiracao, estado, metodo_pagamento, desconto_aplicado, tipo_bilhete_id_tipo, cliente_pessoa_id) VALUES
(1004, '2025-04-10', 1.50, NULL, NULL, '2025-04-10', NULL, 'ativo', 'wallet', 0, 1, 6);
-- Cliente 7 compra monthly_student para linha 1 (usará promoção futura, mas sem desconto agora)
INSERT INTO bilhete (id, data_compra, preco_compra, data_inicio_validade, data_fim_validade, data_viagem, data_expiracao, estado, metodo_pagamento, desconto_aplicado, tipo_bilhete_id_tipo, cliente_pessoa_id) VALUES
(1005, '2025-04-10', 20.00, '2025-04-10', '2025-05-10', NULL, NULL, 'ativo', 'card', 0, 4, 7);

-- 11. VALIDACAO (uso dos bilhetes em viagens)
-- Bilhete 1001 (single) validado na viagem 101, paragem Portagem (ida)
INSERT INTO validacao (data_hora, bilhete_id, viagem_id, paragem_id) VALUES
('2025-04-10 08:12:00', 1001, 101, 1);
-- Bilhete 1002 (daily) validado duas vezes no mesmo dia
INSERT INTO validacao (data_hora, bilhete_id, viagem_id, paragem_id) VALUES
('2025-04-10 08:00:00', 1002, 201, 1),
('2025-04-10 10:30:00', 1002, 202, 3);
-- Bilhete 1003 (monthly) validado várias vezes
INSERT INTO validacao (data_hora, bilhete_id, viagem_id, paragem_id) VALUES
('2025-04-09 08:00:00', 1003, 301, 6),
('2025-04-09 18:00:00', 1003, 303, 1),
('2025-04-10 07:15:00', 1003, 301, 6);
-- Bilhete 1004 (single) será validado depois, mas deixamos sem validação para testar estado 'ativo'

-- 12. AVISO e AVISO_CLIENTE
INSERT INTO aviso (id, titulo, mensagem, data_emissao, administrador_pessoa_id) VALUES
(1, 'Strike Notice', 'Possible delays between 10:00 and 13:00', '2025-04-09', 2),
(2, 'Maintenance', 'Line 2 closed on weekend', '2025-04-08', 1);

INSERT INTO aviso_cliente (data_entrega, data_leitura, lido, aviso_id, cliente_pessoa_id) VALUES
('2025-04-09', NULL, FALSE, 1, 3),
('2025-04-09', '2025-04-09', TRUE, 1, 4),
('2025-04-08', NULL, FALSE, 2, 5);

-- 13. INTERRUPCAO_LINHA
INSERT INTO interrupcao_linha (id_interrupcao, data_inicio, data_fim, motivo, estado, administrador_pessoa_id, linha_id) VALUES
(1, '2025-04-15', '2025-04-16', 'Manutenção da via', TRUE, 2, 1),
(2, '2025-04-20', '2025-04-20', 'Evento cultural', FALSE, 1, 2);