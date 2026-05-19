-- 01_insert_users.sql

-- 1. PESSOA
INSERT INTO pessoa (id, nome, email, username, password_hash) VALUES
(1, 'Super Admin', 'super@metromondego.pt', 'superadmin', 'hash_super'),
(2, 'Admin Operações', 'admin1@metromondego.pt', 'admin1', 'hash_admin1'),
(3, 'Ana Costa', 'ana.costa@email.pt', 'anacosta', 'hash_ana'),
(4, 'Bruno Silva', 'bruno.s@email.pt', 'brunosilva', 'hash_bruno'),
(5, 'Carla Mendes', 'carla.m@email.pt', 'carlam', 'hash_carla'),
(6, 'Diogo Santos', 'diogo.s@email.pt', 'diogos', 'hash_diogo'),
(7, 'Elisa Pereira', 'elisa.p@email.pt', 'elisap', 'hash_elisa');

-- 2. CLIENTE
INSERT INTO cliente (wallet, nif, telefone, pessoa_id) VALUES
(50.00, '123456789', '910000001', 3),
(20.00, '234567890', '910000002', 4),
(100.00, '345678901', '910000003', 5),
(5.00, '456789012', '910000004', 6),
(75.50, '567890123', '910000005', 7);

-- 3. ADMINISTRADOR
INSERT INTO administrador (is_super, pessoa_id) VALUES
(TRUE, 1),
(FALSE, 2);

-- Atualizar sequência
SELECT setval(pg_get_serial_sequence('pessoa', 'id'), COALESCE((SELECT MAX(id) FROM pessoa), 1), TRUE);
