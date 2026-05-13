-- a) Adicionar coluna linha_id ao bilhete (NULL = válido para todas as linhas)
ALTER TABLE bilhete ADD COLUMN linha_id BIGINT;
ALTER TABLE bilhete ADD CONSTRAINT bilhete_linha_fk FOREIGN KEY (linha_id) REFERENCES linha(id);

-- b) Reestruturar a tabela validacao para permitir viagem_id NULL
--    (substituir a PK por uma coluna serial)
ALTER TABLE validacao DROP CONSTRAINT validacao_pkey;
ALTER TABLE validacao ADD COLUMN id SERIAL PRIMARY KEY;
ALTER TABLE validacao ALTER COLUMN viagem_id DROP NOT NULL;
-- Manter a FK para viagem, que agora pode ser NULL