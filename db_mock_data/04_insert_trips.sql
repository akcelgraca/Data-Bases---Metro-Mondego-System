-- 1. VIAGEM
INSERT INTO viagem (id, data_hora_partida, direcao, capacidade_disponivel, atraso_estimado, linha_id) VALUES
(101, CURRENT_DATE + TIME '08:10:00', 'ida', 50, 0, 1),
(102, CURRENT_DATE + TIME '08:30:00', 'ida', 48, 2, 1),
(103, CURRENT_DATE + TIME '08:50:00', 'ida', 50, 0, 1),
(104, CURRENT_DATE + TIME '08:20:00', 'volta', 50, 0, 1),
(105, CURRENT_DATE + TIME '08:40:00', 'volta', 50, 0, 1);

INSERT INTO viagem (id, data_hora_partida, direcao, capacidade_disponivel, atraso_estimado, linha_id) VALUES
(201, CURRENT_DATE + TIME '07:45:00', 'ida', 45, 0, 2),
(202, CURRENT_DATE + TIME '08:15:00', 'ida', 50, 0, 2),
(203, CURRENT_DATE + TIME '07:50:00', 'volta', 50, 0, 2);

INSERT INTO viagem (id, data_hora_partida, direcao, capacidade_disponivel, atraso_estimado, linha_id) VALUES
(301, CURRENT_DATE + TIME '07:00:00', 'ida', 50, 0, 3),
(302, CURRENT_DATE + TIME '08:30:00', 'ida', 50, 0, 3),
(303, CURRENT_DATE + TIME '08:00:00', 'volta', 50, 0, 3),
(304, CURRENT_DATE + TIME '09:30:00', 'volta', 50, 0, 3);

-- Atualizar sequências
SELECT setval(pg_get_serial_sequence('viagem', 'id'), COALESCE((SELECT MAX(id) FROM viagem), 1), TRUE);
