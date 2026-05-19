-- 02_insert_network.sql

-- 1. LINHA
INSERT INTO linha (id, nome, hora_inicio, hora_fim, frequencia, capacidade_default) VALUES
(1, 'Portagem - Hospital', '07:30:00', '21:00:00', 20, 50),
(2, 'Portagem - Estacao B', '07:45:00', '19:00:00', 30, 50),
(3, 'Portagem - Miranda do Corvo - Lousa', '07:00:00', '19:00:00', 90, 50);

-- 2. PARAGEM
INSERT INTO paragem (id, nome) VALUES
(1, 'Portagem'),
(2, 'Hospital'),
(3, 'Estacao B'),
(4, 'Miranda do Corvo'),
(5, 'Lousa'),
(6, 'Serpins');

-- 3. TRAJETO
-- Linha 1: Portagem -> Hospital (ida)
INSERT INTO trajeto (sequencia, tempo_previsto_desde_origem, distancia_acumulada, plataforma_sentido, linha_id, paragem_id) VALUES
(1, 0, 0.0, 'A', 1, 1),
(2, 15, 8.5, 'A', 1, 2);
-- Linha 1 (volta): Hospital -> Portagem
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
