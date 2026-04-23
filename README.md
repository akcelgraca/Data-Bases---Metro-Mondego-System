# Metro Mondego – Sistema de Bilhética e Mobilidade

Projeto desenvolvido no âmbito da unidade curricular de **Bases de Dados** (Licenciatura em Engenharia Informática, 2025/2026) da Universidade de Coimbra.

O sistema engloba:
- Modelação conceptual e física de uma base de dados relacional para o Metro Mondego.
- API REST em Python (Flask) para acesso e manipulação dos dados.
- Autenticação e autorização com JSON Web Tokens (JWT).

---

## Descrição geral

O **Metro Mondego** é uma empresa de mobilidade urbana que necessita de um sistema digital para:
- Consulta de linhas, horários e disponibilidade em tempo real.
- Compra e validação de bilhetes/passes (single trip, daily, monthly, etc.).
- Gestão de clientes, administradores e super administradores.
- Emissão de avisos e interrupções.
- Relatórios analíticos (picos de procura, top spenders, relatórios mensais).

A solução proposta inclui uma base de dados normalizada e uma API REST que segue os requisitos do enunciado do projeto.

---

## Modelação da Base de Dados

### Diagrama Entidade-Relacionamento (E-R)

O modelo conceptual foi criado com a ferramenta **ONDA** e inclui:

- **Entidades fortes:** Pessoa, Linha, Paragem, Viagem, Tipo_Bilhete, Promocao, Aviso, Carregamento, Interrupcao_Linha.
- **Entidades fracas:** Trajeto (depende de Linha), Historico_Preco (depende de Tipo_Bilhete), Validacao (depende de Bilhete e Viagem), Aviso_Cliente (depende de Aviso e Cliente).
- **Especialização total e disjunta:** Pessoa → Cliente, Pessoa → Administrador. Super Administrador é um administrador com `is_super = True`.
- **Relacionamentos:** todos os requisitos do negócio foram modelados (compra de bilhetes, validação de bilhetes em viagens e paragens, carregamentos de carteira, emissão de avisos, interrupções de linhas, promoções aplicáveis a linha e tipo de bilhete, etc.).

A exportação do ONDA (JSON) e as imagens do diagrama E-R estão disponíveis na pasta `docs/`.


