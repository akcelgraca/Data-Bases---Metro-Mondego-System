CREATE TABLE cliente (
	wallet	 FLOAT(8),
	nif	 VARCHAR(512),
	telefone	 VARCHAR(512),
	pessoa_id BIGINT,
	PRIMARY KEY(pessoa_id)
);

CREATE TABLE pessoa (
	id		 BIGINT,
	nome		 VARCHAR(512),
	email	 VARCHAR(512),
	username	 VARCHAR(512),
	password_hash VARCHAR(512),
	PRIMARY KEY(id)
);

CREATE TABLE administrador (
	is_super	 BOOL,
	pessoa_id BIGINT,
	PRIMARY KEY(pessoa_id)
);

CREATE TABLE trajeto (
	sequencia			 INTEGER,
	tempo_previsto_desde_origem INTEGER,
	distancia_acumulada	 FLOAT(8),
	plataforma_sentido		 VARCHAR(512),
	linha_id			 BIGINT,
	paragem_id			 BIGINT NOT NULL,
	PRIMARY KEY(sequencia,linha_id)
);

CREATE TABLE linha (
	id		 BIGINT,
	nome		 VARCHAR(512),
	hora_inicio	 TIMESTAMP,
	hora_fim		 TIMESTAMP,
	frequencia	 BIGINT,
	capacidade_default BIGINT,
	PRIMARY KEY(id)
);

CREATE TABLE paragem (
	id	 BIGINT,
	nome VARCHAR(512),
	PRIMARY KEY(id)
);

CREATE TABLE viagem (
	id			 BIGINT,
	data_hora_partida	 TIMESTAMP,
	direcao		 VARCHAR(512),
	capacidade_disponivel BIGINT,
	atraso_estimado	 BIGINT,
	linha_id		 BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE tipo_bilhete (
	id_tipo BIGINT,
	nome	 VARCHAR(512),
	PRIMARY KEY(id_tipo)
);

CREATE TABLE bilhete (
	id			 BIGINT,
	data_compra		 DATE,
	preco_compra	 FLOAT(8),
	data_inicio_validade DATE,
	data_fim_validade	 DATE,
	data_viagem		 DATE,
	data_expiracao	 DATE,
	estado		 VARCHAR(512),
	metodo_pagamento	 VARCHAR(512),
	desconto_aplicado	 INTEGER,
	tipo_bilhete_id_tipo BIGINT NOT NULL,
	cliente_pessoa_id	 BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE validacao (
	data_hora	 TIMESTAMP,
	bilhete_id BIGINT,
	viagem_id	 BIGINT,
	paragem_id BIGINT NOT NULL,
	PRIMARY KEY(bilhete_id,viagem_id)
);

CREATE TABLE promocao (
	id_promocao		 INTEGER,
	nome		 VARCHAR(512),
	desconto		 INTEGER,
	data_inicio		 DATE,
	data_fim		 DATE,
	tipo_bilhete_id_tipo BIGINT NOT NULL,
	linha_id		 BIGINT NOT NULL,
	PRIMARY KEY(id_promocao)
);

CREATE TABLE aviso (
	id			 BIGINT,
	titulo			 VARCHAR(512),
	mensagem		 VARCHAR(512),
	data_emissao		 DATE,
	administrador_pessoa_id BIGINT NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE carregamento (
	id_carregamento	 INTEGER,
	valor		 FLOAT(8),
	metodo_pagamento	 VARCHAR(512),
	data_hora	 TIMESTAMP,
	cliente_pessoa_id BIGINT NOT NULL,
	PRIMARY KEY(id_carregamento)
);

CREATE TABLE historico_preco (
	preco		 FLOAT(8),
	data_efetiva	 DATE,
	tipo_bilhete_id_tipo BIGINT,
	PRIMARY KEY(data_efetiva,tipo_bilhete_id_tipo)
);

CREATE TABLE aviso_cliente (
	data_entrega	 DATE,
	data_leitura	 DATE,
	lido		 BOOL,
	aviso_id		 BIGINT,
	cliente_pessoa_id BIGINT,
	PRIMARY KEY(aviso_id,cliente_pessoa_id)
);

CREATE TABLE interrupcao_linha (
	id_interrupcao		 INTEGER,
	data_inicio		 DATE,
	data_fim		 DATE,
	motivo			 VARCHAR(512),
	estado			 BOOL,
	administrador_pessoa_id BIGINT NOT NULL,
	linha_id		 BIGINT NOT NULL,
	PRIMARY KEY(id_interrupcao)
);

ALTER TABLE cliente ADD CONSTRAINT cliente_fk1 FOREIGN KEY (pessoa_id) REFERENCES pessoa(id);
ALTER TABLE pessoa ADD UNIQUE (email, username);
ALTER TABLE administrador ADD CONSTRAINT administrador_fk1 FOREIGN KEY (pessoa_id) REFERENCES pessoa(id);
ALTER TABLE trajeto ADD CONSTRAINT trajeto_fk1 FOREIGN KEY (linha_id) REFERENCES linha(id);
ALTER TABLE trajeto ADD CONSTRAINT trajeto_fk2 FOREIGN KEY (paragem_id) REFERENCES paragem(id);
ALTER TABLE viagem ADD CONSTRAINT viagem_fk1 FOREIGN KEY (linha_id) REFERENCES linha(id);
ALTER TABLE bilhete ADD CONSTRAINT bilhete_fk1 FOREIGN KEY (tipo_bilhete_id_tipo) REFERENCES tipo_bilhete(id_tipo);
ALTER TABLE bilhete ADD CONSTRAINT bilhete_fk2 FOREIGN KEY (cliente_pessoa_id) REFERENCES cliente(pessoa_id);
ALTER TABLE validacao ADD CONSTRAINT validacao_fk1 FOREIGN KEY (bilhete_id) REFERENCES bilhete(id);
ALTER TABLE validacao ADD CONSTRAINT validacao_fk2 FOREIGN KEY (viagem_id) REFERENCES viagem(id);
ALTER TABLE validacao ADD CONSTRAINT validacao_fk3 FOREIGN KEY (paragem_id) REFERENCES paragem(id);
ALTER TABLE promocao ADD CONSTRAINT promocao_fk1 FOREIGN KEY (tipo_bilhete_id_tipo) REFERENCES tipo_bilhete(id_tipo);
ALTER TABLE promocao ADD CONSTRAINT promocao_fk2 FOREIGN KEY (linha_id) REFERENCES linha(id);
ALTER TABLE aviso ADD CONSTRAINT aviso_fk1 FOREIGN KEY (administrador_pessoa_id) REFERENCES administrador(pessoa_id);
ALTER TABLE carregamento ADD CONSTRAINT carregamento_fk1 FOREIGN KEY (cliente_pessoa_id) REFERENCES cliente(pessoa_id);
ALTER TABLE historico_preco ADD CONSTRAINT historico_preco_fk1 FOREIGN KEY (tipo_bilhete_id_tipo) REFERENCES tipo_bilhete(id_tipo);
ALTER TABLE aviso_cliente ADD CONSTRAINT aviso_cliente_fk1 FOREIGN KEY (aviso_id) REFERENCES aviso(id);
ALTER TABLE aviso_cliente ADD CONSTRAINT aviso_cliente_fk2 FOREIGN KEY (cliente_pessoa_id) REFERENCES cliente(pessoa_id);
ALTER TABLE interrupcao_linha ADD CONSTRAINT interrupcao_linha_fk1 FOREIGN KEY (administrador_pessoa_id) REFERENCES administrador(pessoa_id);
ALTER TABLE interrupcao_linha ADD CONSTRAINT interrupcao_linha_fk2 FOREIGN KEY (linha_id) REFERENCES linha(id);

