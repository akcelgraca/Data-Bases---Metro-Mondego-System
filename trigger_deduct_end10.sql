-- Função que deduz o saldo da carteira no momento da compra
CREATE OR REPLACE FUNCTION func_deduct_wallet()
RETURNS TRIGGER AS $$
DECLARE
    current_balance FLOAT;
BEGIN
    -- Lê o saldo actual da carteira
    SELECT wallet INTO current_balance
    FROM cliente
    WHERE pessoa_id = NEW.cliente_pessoa_id;

    -- Se o saldo for insuficiente, rejeita a compra
    IF current_balance < NEW.preco_compra THEN
        RAISE EXCEPTION 'Saldo insuficiente para a compra.';
    END IF;

    -- Deduz o valor da carteira
    UPDATE cliente
    SET wallet = wallet - NEW.preco_compra
    WHERE pessoa_id = NEW.cliente_pessoa_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger chamado antes de cada INSERT na tabela bilhete
CREATE TRIGGER trigger_deduct_wallet
BEFORE INSERT ON bilhete
FOR EACH ROW
EXECUTE FUNCTION func_deduct_wallet();