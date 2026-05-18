##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2025/2026 ===============
## =============================================
## =================== Projeto ====================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors:
##   Akcel, Martim, Tiago
##   BD 2025/2026 Team
##   University of Coimbra


import flask
import logging
import psycopg2
import jwt
import datetime
from functools import wraps

app = flask.Flask(__name__)

# Logger definido ao nível do módulo para estar disponível em todos os endpoints.
# Se ficar dentro do 'if __name__ == __main__', o Flask em modo debug reinicia o processo
# e o logger fica inacessível, causando NameError.
logging.basicConfig(filename='log_file.log')
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)

# CONFIGURAÇÃO DA CHAVE SECRETA PARA JWT - Adicionei
app.config['SECRET_KEY'] = 'chave_super_secreta_do_projeto'   # podes alterar, mas mantém secreta

StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(
        user='postgres',
        password='postgres',
        host='127.0.0.1',
        port='5432',
        database='metro'
    )

    return db

##########################################################
## FUNÇÕES AUXILIARES DE AUTENTICAÇÃO
##########################################################

def generate_token(user_id, username, is_admin, is_super=False):
    """
    Gera um JWT com validade de 2 horas.
    O token contém o user_id, username, e flags de permissão (is_admin, is_super).
    Este token será enviado ao cliente e deve ser incluído no header
    'Authorization: Bearer <token>' em todos os pedidos seguintes.
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'is_super': is_super,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }

    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

    # compatibilidade com versões diferentes do PyJWT
    if isinstance(token, bytes):
        token = token.decode('utf-8')

    return token



def token_required(f):
    """
    Decorador para proteger endpoints que requerem autenticação.
    Lê o token do header 'Authorization: Bearer <token>', valida-o
    e passa os dados do utilizador à função do endpoint como 'current_user'.
    Se o token estiver em falta, expirado ou inválido, devolve erro 400.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in flask.request.headers:
            auth_header = flask.request.headers['Authorization']
            logger.debug(f'Authorization header recebido: {auth_header}')
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            return flask.jsonify({'status': 400, 'errors': 'Token em falta'}), 400

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data
            logger.debug(f'Token válido para user={current_user.get("username")}')
        except jwt.ExpiredSignatureError:
            return flask.jsonify({'status': 400, 'errors': 'Token expirado'}), 400
        except jwt.InvalidTokenError as e:
            logger.error(f'Token inválido: {str(e)}')
            return flask.jsonify({'status': 400, 'errors': 'Token inválido'}), 400

        return f(current_user, *args, **kwargs)

    return decorated



##########################################################
## ENDPOINTS
##########################################################

##
## Endpoint 1 — Autenticação
##
## Recebe username e password, verifica na BD e devolve um token JWT.
## O token deve ser guardado pelo cliente e enviado no header
## 'Authorization: Bearer <token>' em todos os pedidos seguintes.
##
## Método: PUT
## URL: http://localhost:8080/dbproj/user
## Body: {"username": "superadmin", "password": "hash_super"}
## Resposta: {"status": 200, "results": "<token>"}
##

@app.route('/dbproj/user', methods=['PUT'])
def login():
    logger.info('PUT /dbproj/user')
    payload = flask.request.get_json(silent=True)

    # validação do payload - verificar que é JSON e que tem os campos necessários
    if not payload or 'username' not in payload or 'password' not in payload:
        return flask.jsonify({'status': 400, 'errors': 'Username e password são obrigatórios'}), 400

    # guardar username e password em variáveis
    username = payload['username']  
    password = payload['password']

    conn = db_connection()
    cur = conn.cursor()

    try:
        # Faz JOIN com administrador para saber se o utilizador é admin e se é super admin.
        # LEFT JOIN garante que clientes normais (sem entrada em administrador) também são encontrados.
        cur.execute("""
            SELECT p.id, p.username, p.password_hash,
                   a.pessoa_id IS NOT NULL AS is_admin,
                   a.is_super
            FROM pessoa p
            LEFT JOIN administrador a ON p.id = a.pessoa_id
            WHERE p.username = %s
        """, (username,))
        user = cur.fetchone()

        if user is None:
            return flask.jsonify({'status': 400, 'errors': 'Credenciais inválidas'}), 400

        user_id, db_username, db_password_hash, is_admin, is_super = user

        # Comparação direta da password (os dados de teste têm passwords em texto simples).
        if db_password_hash != password:
            return flask.jsonify({'status': 400, 'errors': 'Credenciais inválidas'}), 400

        token = generate_token(user_id, db_username, is_admin, is_super)
        logger.debug(f'Login bem-sucedido para {db_username}, admin={is_admin}, super={is_super}')

        response = {'status': 200, 'results': token}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'PUT /dbproj/user - error: {error}')
        response = {'status': 500, 'errors': str(error)}
    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)

##
## Endpoint 2 — Adicionar Administrador (Super Admin only)
##
## Cria um novo administrador (pessoa + administrador).
## Apenas utilizadores com o token de Super Admin podem aceder.
##
## Método: PUT
## URL: http://localhost:8080/dbproj/register/admin
## Body: {"name": "Nome", "email": "admin@exemplo.pt", "password": "secret"}
## Resposta: {"status": 200, "results": {"user_id": <id>}}
##
@app.route('/dbproj/register/admin', methods=['PUT'])
@token_required
def add_administrator(current_user):
    logger.info('PUT /dbproj/register/admin')

    if not current_user.get('is_super'):
        logger.warning(f'Acesso negado para {current_user["username"]}')
        return flask.jsonify({'status': 400, 'errors': 'Apenas o Super Admin pode criar administradores'}), 400

    logger.debug(
        f'Content-Type recebido: {flask.request.content_type}; '
        f'is_json={flask.request.is_json}'
    )
    payload = flask.request.get_json(silent=True)
    if not payload:
        raw_body = flask.request.get_data(as_text=True)
        logger.warning(f'Payload inválido ou ausente. Body bruto recebido: {raw_body!r}')
        return flask.jsonify({'status': 400, 'errors': 'Payload em falta ou JSON inválido'}), 400

    name = payload.get('name')
    email = payload.get('email')
    password = payload.get('password')

    if not all([name, email, password]):
        logger.warning(f'Campos obrigatórios em falta no payload: {payload}')
        return flask.jsonify({'status': 400, 'errors': 'Campos name, email e password são obrigatórios'}), 400

    username = email
    password_hash = password

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM pessoa WHERE email = %s OR username = %s", (email, username))
        if cur.fetchone():
            logger.warning(f'Tentativa de registo com email/username já existente: {email}')
            return flask.jsonify({'status': 400, 'errors': 'Email ou username já em uso'}), 400

        statement = '''
            INSERT INTO pessoa (nome, email, username, password_hash)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        '''
        cur.execute(statement, (name, email, username, password_hash))
        new_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO administrador (is_super, pessoa_id) VALUES (FALSE, %s)",
            (new_id,)
        )

        conn.commit()
        logger.debug(f'Administrador criado: id={new_id}, nome={name}, email={email}')

        response = {
            'status': StatusCodes['success'],
            'errors': None,
            'results': {'user_id': new_id}
        }

    except psycopg2.IntegrityError as error:
        conn.rollback()
        logger.error(f'Erro de integridade: {error}')
        response = {
            'status': StatusCodes['api_error'],
            'errors': 'Email ou username já em uso'
        }

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'PUT /dbproj/register/admin - erro: {error}')
        response = {
            'status': StatusCodes['internal_error'],
            'errors': str(error)
        }

    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)

##
## Endpoint 3 — Adicionar Cliente (Admin only)
##
## Cria um novo cliente (pessoa + cliente).
## Apenas utilizadores com o token de Administrador podem aceder.
##
## Método: POST
## URL: http://localhost:8080/dbproj/register/customer
## Body: {"name": "Customer Name", "nif": "123456789", "telefone": "910000000", "email": "customer@email.pt", "password": "secret"}
## Resposta: {"status": 200, "results": {"user_id": <id>}}
##

@app.route('/dbproj/register/customer', methods=['POST'])
@token_required
def add_customer(current_user):
    logger.info('POST /dbproj/register/customer')

    # 1. Verificar permissão – qualquer administrador pode criar clientes
    if not current_user.get('is_admin'):
        logger.warning(f'Acesso negado para {current_user["username"]} (não é admin)')
        return flask.jsonify({'status': 400, 'errors': 'Apenas administradores podem criar clientes'}), 400

    # 2. Validar payload
    payload = flask.request.get_json(silent=True)
    if not payload:
        logger.warning('Payload inválido ou ausente')
        return flask.jsonify({'status': 400, 'errors': 'Payload em falta ou JSON inválido'}), 400

    name = payload.get('name')
    email = payload.get('email')
    password = payload.get('password')
    nif = payload.get('nif')
    telefone = payload.get('telefone')

    if not all([name, email, password, nif, telefone]):
        logger.warning(f'Campos obrigatórios em falta: {payload}')
        return flask.jsonify({'status': 400, 'errors': 'Campos name, email, password, nif e telefone são obrigatórios'}), 400

    # 3. Preparar dados
    username = email                     # design: username = email
    password_hash = password            # ainda sem hashing (testes)
    initial_wallet = 0.00               # cliente começa com saldo zero

    conn = db_connection()
    cur = conn.cursor()

    try:
        # Verificar unicidade do email/username
        cur.execute("SELECT id FROM pessoa WHERE email = %s OR username = %s", (email, username))
        if cur.fetchone():
            logger.warning(f'Email/username já em uso: {email}')
            return flask.jsonify({'status': 400, 'errors': 'Email ou username já em uso'}), 400

        # Inserir em pessoa
        statement = '''
            INSERT INTO pessoa (nome, email, username, password_hash)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        '''
        cur.execute(statement, (name, email, username, password_hash))
        new_id = cur.fetchone()[0]

        # Inserir em cliente (wallet inicial = 0.0)
        cur.execute(
            "INSERT INTO cliente (wallet, nif, telefone, pessoa_id) VALUES (%s, %s, %s, %s)",
            (initial_wallet, nif, telefone, new_id)
        )

        conn.commit()
        logger.debug(f'Cliente criado: id={new_id}, nome={name}, email={email}')

        response = {
            'status': StatusCodes['success'],
            'errors': None,
            'results': {'user_id': new_id}
        }

    except psycopg2.IntegrityError as error:
        conn.rollback()
        logger.error(f'Erro de integridade: {error}')
        response = {
            'status': StatusCodes['api_error'],
            'errors': 'Email ou username já em uso'
        }

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/register/customer - erro: {error}')
        response = {
            'status': StatusCodes['internal_error'],
            'errors': str(error)
        }

    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)

##
## Endpoint 4 — Atualizar configurações de operação de uma linha (Admin only)
##
## Atualiza os parâmetros operacionais de uma linha (hora de início, fim, frequência, capacidade).
## Apenas administradores podem aceder.
##
## Método: PUT
## URL: http://localhost:8080/dbproj/line_operation/{line_id}
## Body: {"start_time": "07:30:00", "end_time": "21:00:00", "frequency_minutes": 20, "vehicle_capacity": 50}
## Resposta: {"status": 200, "errors": null} ou {"status": 400, "errors": "mensagem"}
##

@app.route('/dbproj/line_operation/<int:line_id>', methods=['PUT'])
@token_required
def update_line_operation(current_user, line_id):
    logger.info('PUT /dbproj/line_operation/%s', line_id)

    # 1. Verificar permissão – qualquer administrador
    if not current_user.get('is_admin'):
        logger.warning(f'Acesso negado para {current_user["username"]} (não é admin)')
        return flask.jsonify({'status': 400, 'errors': 'Apenas administradores podem alterar linhas'}), 400

    # 2. Validar payload
    payload = flask.request.get_json(silent=True)
    if not payload:
        return flask.jsonify({'status': 400, 'errors': 'Payload em falta ou JSON inválido'}), 400

    start_time = payload.get('start_time')
    end_time = payload.get('end_time')
    frequency = payload.get('frequency_minutes')
    capacity = payload.get('vehicle_capacity')

    if not all([start_time, end_time, frequency is not None, capacity is not None]):
        logger.warning(f'Campos obrigatórios em falta: {payload}')
        return flask.jsonify({'status': 400, 'errors': 'Campos start_time, end_time, frequency_minutes e vehicle_capacity são obrigatórios'}), 400

    # Validar que frequency e capacity são inteiros positivos
    try:
        frequency = int(frequency)
        capacity = int(capacity)
        if frequency <= 0 or capacity <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return flask.jsonify({'status': 400, 'errors': 'frequency_minutes e vehicle_capacity devem ser inteiros positivos'}), 400

    conn = db_connection()
    cur = conn.cursor()

    try:
        # Verificar se a linha existe
        cur.execute("SELECT id FROM linha WHERE id = %s", (line_id,))
        if cur.fetchone() is None:
            return flask.jsonify({'status': 400, 'errors': f'Linha com id {line_id} não encontrada'}), 400

        # Atualizar os campos
        statement = """
            UPDATE linha
            SET hora_inicio = %s,
                hora_fim = %s,
                frequencia = %s,
                capacidade_default = %s
            WHERE id = %s
        """
        cur.execute(statement, (start_time, end_time, frequency, capacity, line_id))

        if cur.rowcount == 0:
            # Não deveria acontecer porque verificámos a existência, mas por segurança
            conn.rollback()
            return flask.jsonify({'status': 400, 'errors': 'Nenhuma linha atualizada'}), 400

        conn.commit()
        logger.debug(f'Linha {line_id} atualizada: start={start_time}, end={end_time}, freq={frequency}, cap={capacity}')

        response = {'status': StatusCodes['success'], 'errors': None}

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'PUT /dbproj/line_operation/{line_id} - erro: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)

##
## Endpoint 5 — Atualizar preço de um tipo de bilhete (Admin only)
##
## Insere uma nova entrada no histórico de preços para o tipo de bilhete indicado.
## Apenas administradores podem aceder.
##
## Método: PUT
## URL: http://localhost:8080/dbproj/fares/{fare_id}
## Body: {"price": 2.75, "effective_from": "2025-06-01"}
## Resposta: {"status": 200, "errors": null} ou {"status": 400, "errors": "mensagem"}
##

@app.route('/dbproj/fares/<int:fare_id>', methods=['PUT'])
@token_required
def update_fare_price(current_user, fare_id):
    logger.info('PUT /dbproj/fares/%s', fare_id)

    # 1. Verificar permissão – apenas administradores
    if not current_user.get('is_admin'):
        logger.warning(f'Acesso negado para {current_user["username"]} (não é admin)')
        return flask.jsonify({'status': 400, 'errors': 'Apenas administradores podem alterar tarifas'}), 400

    # 2. Validar payload
    payload = flask.request.get_json(silent=True)
    if not payload:
        return flask.jsonify({'status': 400, 'errors': 'Payload em falta ou JSON inválido'}), 400

    price = payload.get('price')
    effective_from = payload.get('effective_from')

    if not price or not effective_from:
        return flask.jsonify({'status': 400, 'errors': 'Campos price e effective_from são obrigatórios'}), 400

    # Validar price (número positivo)
    try:
        price = float(price)
        if price <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return flask.jsonify({'status': 400, 'errors': 'price deve ser um número positivo'}), 400

    conn = db_connection()
    cur = conn.cursor()

    try:
        # Verificar se o tipo_bilhete existe
        cur.execute("SELECT id_tipo FROM tipo_bilhete WHERE id_tipo = %s", (fare_id,))
        if cur.fetchone() is None:
            return flask.jsonify({'status': 400, 'errors': f'Tipo de bilhete com id {fare_id} não encontrado'}), 400

        # Inserir novo preço no histórico (a chave primária composta garante que não há duplicados da mesma data)
        cur.execute(
            "INSERT INTO historico_preco (preco, data_efetiva, tipo_bilhete_id_tipo) VALUES (%s, %s, %s)",
            (price, effective_from, fare_id)
        )

        conn.commit()
        logger.debug(f'Preço atualizado para tipo_bilhete {fare_id}: {price} a partir de {effective_from}')

        response = {'status': StatusCodes['success'], 'errors': None}

    except psycopg2.IntegrityError as error:
        conn.rollback()
        logger.error(f'Erro de integridade: {error}')
        # Possível duplicado (mesma data para o mesmo tipo) ou violação de FK
        if 'unique' in str(error).lower():
            response = {'status': StatusCodes['api_error'], 'errors': 'Já existe um preço para esta data e tipo de bilhete'}
        else:
            response = {'status': StatusCodes['api_error'], 'errors': 'Erro de integridade'}

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'PUT /dbproj/fares/{fare_id} - erro: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)


##
## Endpoint 6 - Broadcast Aviso
##
## Envia um aviso geral para todos os utilizadores
##
## Método: POST
## URL: http://localhost:8080/dbproj/notices/broadcast
## Body: {"title": "Strike Notice", "message": "Possible delays between 10:00 and 13:00"}
## Resposta: {"status": 200, "errors": null} ou {"status": 400, "errors": "mensagem"}
##

@app.route('/dbproj/notices/broadcast', methods=['POST'])
@token_required
def broadcast_notice(current_user):
    logger.info('POST /dbproj/notices/broadcast')

    # Verificar permissão - apenas administradores podem enviar avisos
    if not current_user.get('is_admin'):
        logger.warning(f'Acesso negado para {current_user["username"]} (não é admin)')
        return flask.jsonify({'status': 400, 'errors': 'Apenas administradores podem enviar avisos'}), 400

    # Validar payload
    payload = flask.request.get_json(silent=True)
    if not payload:
        return flask.jsonify({'status': 400, 'errors': 'Payload em falta ou JSON invalido'}), 400

    title = payload.get('title')
    message = payload.get('message')

    if not title or not message:
        return flask.jsonify({'status': 400, 'errors': 'Campos title e message são obrigatórios'}), 400

    conn = db_connection()
    cur = conn.cursor()

    try:
        admin_id = current_user['user_id']

        # Inserir o aviso na tabela
        insert_aviso_query = """
            INSERT INTO aviso (titulo, mensagem, data_emissao, administrador_pessoa_id)
            VALUES (%s, %s, CURRENT_DATE, %s)
            RETURNING id
        """
        cur.execute(insert_aviso_query, (title, message, admin_id))
        new_aviso_id = cur.fetchone()[0]

        # Broadcast para todos os clientes inserindo em aviso_cliente
        insert_aviso_cliente_query = """
            INSERT INTO aviso_cliente (data_entrega, data_leitura, lido, aviso_id, cliente_pessoa_id)
            SELECT CURRENT_DATE, NULL, FALSE, %s, pessoa_id
            FROM cliente
        """

        cur.execute(insert_aviso_cliente_query, (new_aviso_id,))

        # Commit da transação após ambas as operações terem sido executadas
        conn.commit()
        logger.debug(f'Aviso broadcast criado: id={new_aviso_id}, title={title} enviado para todos os clientes pelo admin id={admin_id}.')

        response = {'status': StatusCodes['success'], 'errors': None}

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/notices/broadcast - erro: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)


## Endpoint 7 - Criar promoção e regra de desconto (Admin only)
##
## Insere uma nova promoção para que os clientes possam usufruir de descontos em bilhetes
##
## Método: POST
## URL: http://localhost:8080/dbproj/promotions
## Body: {
##  "name": "School Holidays",
##  "line_id": 1,
##  "product_type": "daily",
##  "discount_percent": 20,
##  "start_date": "2025-07-01",
##  "end_date": "2025-07-31"
## }
## Resposta: {"status": 200, "errors": null, "results": {"promotion_id": id}}
##

@app.route('/dbproj/promotions', methods=['POST'])
@token_required
def create_promotion(current_user):
    logger.info('POST /dbproj/promotions')

    # Verificar permissão - apenas administradores podem criar promoções
    if not current_user.get('is_admin'):
        logger.warning(f'Acesso negado para {current_user["username"]}. Não é admin.')
        return flask.jsonify({'status': 400, 'errors': 'Apenas administradores podem criar promoções'}), 400

    # Validar payload
    payload = flask.request.get_json(silent=True)
    if not payload:
        return flask.jsonify({'status': 400, 'errors': 'Payload em falta ou JSON inválido'}), 400

    name = payload.get('name')
    line_id = payload.get('line_id')
    product_type = payload.get('product_type')
    discount_percent = payload.get('discount_percent')
    start_date = payload.get('start_date')
    end_date = payload.get('end_date')

    # Validar campos obrigatórios
    if not all([name, line_id, product_type, discount_percent, start_date, end_date]):
        return flask.jsonify({'status': 400, 'errors': 'Todos os campos são obrigatórios'}), 400

    # Validar se o desconto é um número inteiro válido
    try:
        discount_percent = int(discount_percent)
        if discount_percent <= 0 or discount_percent > 100:
            raise ValueError
    except (ValueError, TypeError):
        return flask.jsonify({'status': 400, 'errors': 'discount_percent deve ser um inteiro entre 1 e 100'}), 400

    conn = db_connection()
    cur = conn.cursor()

    try:
        # Obter o ID do tipo_bilhete a partir da string enviada no payload
        cur.execute("SELECT id_tipo FROM tipo_bilhete WHERE nome = %s", (product_type,))
        tipo_bilhete = cur.fetchone()
        if not tipo_bilhete:
            return flask.jsonify({'status': 400, 'errors': f'Tipo de bilhete "{product_type}" não encontrado'}), 400
        tipo_bilhete_id = tipo_bilhete[0]

        # Verificar se a linha existe
        cur.execute("SELECT id FROM linha WHERE id = %s", (line_id,))
        if cur.fetchone() is None:
            return flask.jsonify({'status': 400, 'errors': f'Linha com id {line_id} não encontrada'}), 400

        # Inserir a nova promoção na base de dados
        insert_query = """
            INSERT INTO promocao (nome, desconto, data_inicio, data_fim, tipo_bilhete_id_tipo, linha_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id_promocao
        """

        cur.execute(insert_query, (name, discount_percent, start_date, end_date, tipo_bilhete_id, line_id))
        new_promotion_id = cur.fetchone()[0]

        # Efetuar o commit da transação
        conn.commit()
        logger.debug(f'Promoção {new_promotion_id} ("{name}") criada com sucesso.')

        response = {
            'status': StatusCodes['success'],
            'errors': None,
            'results': {'promotion_id': new_promotion_id}
        }

    except psycopg2.Error as error:
        conn.rollback()
        logger.error(f'POST /dbproj/promotions - erro de base de dados: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        
    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)

##
## Endpoint 8 — Listar linhas e próximas partidas (Clientes / qualquer autenticado)
##
## Devolve, para cada linha e direção (ida/volta), a próxima viagem com
## capacidade disponível, atraso estimado e os terminais de origem e destino.
##
## Método: GET
## URL: http://localhost:8080/dbproj/lines_next
## Resposta: {"status": 200, "results": [ { ... } ]}
##

@app.route('/dbproj/lines_next', methods=['GET'])
@token_required
def lines_next(current_user):
    logger.info('GET /dbproj/lines_next')

    conn = db_connection()
    cur = conn.cursor()

    try:
        # Obtemos o timestamp atual para passar como parâmetro,
        now_ts = datetime.datetime.now()

        query = """
            SELECT l.id AS line_id,
                   l.nome AS line_name,
                   -- origem = paragem com sequência 1 no sentido certo
                   (SELECT pr.nome FROM paragem pr
                    JOIN trajeto t ON t.paragem_id = pr.id
                    WHERE t.linha_id = l.id
                      AND t.plataforma_sentido = CASE v.direcao
                                                    WHEN 'ida' THEN 'A'
                                                    WHEN 'volta' THEN 'B'
                                                  END
                      AND t.sequencia = 1) AS origin_terminal,
                   -- destino = paragem com a sequência máxima no sentido
                   (SELECT pr.nome FROM paragem pr
                    JOIN trajeto t ON t.paragem_id = pr.id
                    WHERE t.linha_id = l.id
                      AND t.plataforma_sentido = CASE v.direcao
                                                    WHEN 'ida' THEN 'A'
                                                    WHEN 'volta' THEN 'B'
                                                  END
                      AND t.sequencia = (SELECT MAX(t2.sequencia)
                                         FROM trajeto t2
                                         WHERE t2.linha_id = l.id
                                           AND t2.plataforma_sentido =
                                               CASE v.direcao
                                                   WHEN 'ida' THEN 'A'
                                                   WHEN 'volta' THEN 'B'
                                               END)
                   ) AS destination_terminal,
                   v.data_hora_partida AS departure_time,
                   v.atraso_estimado AS estimated_delay_min,
                   v.capacidade_disponivel AS available_capacity
            FROM viagem v
            JOIN linha l ON l.id = v.linha_id
            WHERE v.data_hora_partida >= %s
              AND v.data_hora_partida = (
                  SELECT MIN(v2.data_hora_partida)
                  FROM viagem v2
                  WHERE v2.linha_id = l.id
                    AND v2.direcao = v.direcao
                    AND v2.data_hora_partida >= %s
              )
            ORDER BY l.id, v.direcao;
        """

        cur.execute(query, (now_ts, now_ts))
        rows = cur.fetchall()

        results = []
        for row in rows:
            results.append({
                'line_id': int(row[0]),
                'line_name': row[1],
                'origin_terminal': row[2],
                'destination_terminal': row[3],
                'departure_time': row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else None,
                'estimated_delay_min': int(row[5]) if row[5] is not None else 0,
                'available_capacity': int(row[6]) if row[6] is not None else 0
            })

        response = {'status': StatusCodes['success'], 'errors': None, 'results': results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /dbproj/lines_next - erro: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)

##
## Endpoint 9 — Adicionar fundos à carteira (Cliente autenticado)
##
## Permite que um cliente adicione saldo à sua própria carteira.
##
## Método: POST
## URL: http://localhost:8080/dbproj/wallet/topup
## Body: {"amount": 20.00, "payment_method": "card"}
## Resposta: {"status": 200, "results": {"new_balance": 70.00}}
##

@app.route('/dbproj/wallet/topup', methods=['POST'])
@token_required
def wallet_topup(current_user):
    logger.info('POST /dbproj/wallet/topup')

    # Apenas clientes podem carregar a carteira
    if current_user.get('is_admin'):
        logger.warning(f'Administrador {current_user["username"]} tentou carregar carteira.')
        return flask.jsonify({'status': 400, 'errors': 'Apenas clientes podem carregar a carteira'}), 400

    payload = flask.request.get_json(silent=True)
    if not payload:
        return flask.jsonify({'status': 400, 'errors': 'Payload em falta ou JSON inválido'}), 400

    amount = payload.get('amount')
    payment_method = payload.get('payment_method')

    if not amount or not payment_method:
        return flask.jsonify({'status': 400, 'errors': 'Campos amount e payment_method são obrigatórios'}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return flask.jsonify({'status': 400, 'errors': 'amount deve ser um número positivo'}), 400

    user_id = current_user['user_id']

    conn = db_connection()
    cur = conn.cursor()

    try:
        # Verificar que o utilizador é realmente um cliente
        cur.execute("SELECT pessoa_id, wallet FROM cliente WHERE pessoa_id = %s", (user_id,))
        cliente_row = cur.fetchone()
        if not cliente_row:
            return flask.jsonify({'status': 400, 'errors': 'O utilizador autenticado não é um cliente'}), 400

        current_wallet = cliente_row[1]

        # Inserir registo de carregamento
        cur.execute(
            "INSERT INTO carregamento (valor, metodo_pagamento, data_hora, cliente_pessoa_id) "
            "VALUES (%s, %s, %s, %s) RETURNING id_carregamento",
            (amount, payment_method, datetime.datetime.now(), user_id)
        )
        new_carregamento_id = cur.fetchone()[0]

        # Atualizar o saldo da carteira do cliente
        cur.execute(
            "UPDATE cliente SET wallet = wallet + %s WHERE pessoa_id = %s RETURNING wallet", 
            (amount, user_id)
        )
        new_balance = cur.fetchone()[0]

        conn.commit()
        logger.debug(f'Cliente {user_id} carregou {amount:.2f}€. Saldo: {new_balance:.2f}€')

        response = {
            'status': StatusCodes['success'],
            'errors': None,
            'results': {'new_balance': new_balance}
        }

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/wallet/topup - erro: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)

##
## Endpoint 10 — Comprar bilhete/passe (Clientes)
##
## Cria um bilhete (single trip, daily, monthly pass, etc.) e deduz o saldo da carteira.
## Um trigger na BD (trigger_deduct_wallet) trata da dedução.
##
## Método: POST
## URL: http://localhost:8080/dbproj/purchase
## Body: {"line_id": 2, "product_type": "single_trip", "travel_date": "2025-04-12"}
## Resposta: {"status": 200, "results": {"purchase_id": id, "final_price": 1.50}}
##

@app.route('/dbproj/purchase', methods=['POST'])
@token_required
def purchase_ticket(current_user):
    logger.info('POST /dbproj/purchase')

    # 1. Apenas clientes (não administradores)
    if current_user.get('is_admin'):
        logger.warning(f'Administrador {current_user["username"]} tentou comprar bilhete.')
        return flask.jsonify({'status': 400, 'errors': 'Apenas clientes podem comprar bilhetes'}), 400

    payload = flask.request.get_json(silent=True)
    if not payload:
        return flask.jsonify({'status': 400, 'errors': 'Payload em falta ou JSON inválido'}), 400

    line_id = payload.get('line_id')
    product_type = payload.get('product_type')
    travel_date = payload.get('travel_date')

    if not all([line_id, product_type, travel_date]):
        return flask.jsonify({'status': 400, 'errors': 'Campos line_id, product_type e travel_date são obrigatórios'}), 400

    user_id = current_user['user_id']

    conn = db_connection()
    cur = conn.cursor()

    try:
        # 2. Verificar que o utilizador é mesmo um cliente
        cur.execute("SELECT pessoa_id, wallet FROM cliente WHERE pessoa_id = %s", (user_id,))
        cliente_row = cur.fetchone()
        if not cliente_row:
            return flask.jsonify({'status': 400, 'errors': 'Utilizador não é cliente'}), 400

        # 3. Obter ID do tipo de bilhete a partir do nome
        cur.execute("SELECT id_tipo FROM tipo_bilhete WHERE nome = %s", (product_type,))
        tipo_row = cur.fetchone()
        if not tipo_row:
            return flask.jsonify({'status': 400, 'errors': f'Tipo de bilhete "{product_type}" não encontrado'}), 400
        tipo_bilhete_id = tipo_row[0]

        # 4. Obter preço actual (última entrada no historico_preco com data <= hoje)
        cur.execute("""
            SELECT preco FROM historico_preco
            WHERE tipo_bilhete_id_tipo = %s AND data_efetiva <= CURRENT_DATE
            ORDER BY data_efetiva DESC
            LIMIT 1
        """, (tipo_bilhete_id,))
        preco_row = cur.fetchone()
        if not preco_row:
            return flask.jsonify({'status': 400, 'errors': 'Não existe preço definido para este tipo de bilhete'}), 400
        base_price = float(preco_row[0])

        # 5. Verificar se existe promoção activa para esta linha e tipo de bilhete
        cur.execute("""
            SELECT desconto FROM promocao
            WHERE linha_id = %s
              AND tipo_bilhete_id_tipo = %s
              AND CURRENT_DATE BETWEEN data_inicio AND data_fim
            LIMIT 1
        """, (line_id, tipo_bilhete_id))
        promo_row = cur.fetchone()
        discount = promo_row[0] if promo_row else 0

        final_price = base_price * (1 - discount / 100.0)
        # Arredondar a 2 casas decimais
        final_price = round(final_price, 2)

        # 6. Definir datas de validade conforme o tipo de bilhete
        data_viagem = None
        data_inicio = None
        data_fim = None
        data_expiracao = None

        if product_type == 'single_trip':
            data_viagem = travel_date
        elif product_type == 'daily':
            data_inicio = travel_date
            data_fim = travel_date               # válido apenas no próprio dia
        elif product_type in ('monthly_pass', 'monthly_student', 'monthly_senior'):
            data_inicio = travel_date
            # Adicionamos 30 dias como validade de um mês
            data_fim = (datetime.datetime.strptime(travel_date, '%Y-%m-%d') + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        else:
            return flask.jsonify({'status': 400, 'errors': f'Tipo de bilhete "{product_type}" não suportado'}), 400

        # Atualizar carteira do cliente de forma atómica
        update_wallet_query = """
            UPDATE cliente 
            SET wallet = wallet - %s 
            WHERE pessoa_id = %s AND wallet >= %s 
            RETURNING wallet
        """
        cur.execute(update_wallet_query, (final_price, user_id, final_price))
        wallet_result = cur.fetchone()
        
        if wallet_result is None:
            conn.rollback()
            logger.warning(f'Saldo insuficiente para cliente {user_id}')
            return flask.jsonify({'status': StatusCodes['api_error'], 'errors': 'Saldo insuficiente na carteira'}), 400

        # 7. Inserir o bilhete e deixar a BD gerar o ID
        insert_query = """
            INSERT INTO bilhete (data_compra, preco_compra,
                                 data_inicio_validade, data_fim_validade,
                                 data_viagem, data_expiracao, estado,
                                 metodo_pagamento, desconto_aplicado,
                                 tipo_bilhete_id_tipo, cliente_pessoa_id, linha_id)
            VALUES (CURRENT_DATE, %s,
                    %s, %s,
                    %s, %s, 'ativo',
                    'wallet', %s,
                    %s, %s, %s)
            RETURNING id
        """
        cur.execute(insert_query, (
            final_price,
            data_inicio, data_fim,
            data_viagem, data_expiracao,
            discount,                # armazena o desconto aplicado (0 se não houve)
            tipo_bilhete_id,
            user_id,
            line_id
        ))
        new_bilhete_id = cur.fetchone()[0]

        # Se tudo correr bem, fazemos commit das duas operações (UPDATE e INSERT)
        conn.commit()
        logger.debug(f'Bilhete {new_bilhete_id} comprado: tipo={product_type}, linha={line_id}, preço={final_price}')

        response = {
            'status': StatusCodes['success'],
            'errors': None,
            'results': {
                'purchase_id': new_bilhete_id,
                'final_price': final_price
            }
        }

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/purchase - erro: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)

##
## Endpoint 11 — Validar/Usar bilhete (Clientes)
##
## Regista uma validação de bilhete (viagem única, diária, mensal, etc.)
## Verifica se o bilhete está ativo, dentro da validade e válido para a linha.
## Se bilhete single_trip já tiver sido usado, rejeita.
##
## Método: POST
## URL: http://localhost:8080/dbproj/ticket/use/<int:ticket_id>
## Body: {"used_at": "2025-04-12 08:20:00", "station_id": 7}
## Resposta: {"status": 200, "errors": null} ou {"status": 400, "errors": "mensagem"}
##

@app.route('/dbproj/ticket/use/<int:ticket_id>', methods=['POST'])
@token_required
def validate_ticket(current_user, ticket_id):
    logger.info('POST /dbproj/ticket/use/%s', ticket_id)

    # 1. Apenas clientes podem validar bilhetes
    if current_user.get('is_admin'):
        return flask.jsonify({'status': 400, 'errors': 'Apenas clientes podem validar bilhetes'}), 400

    payload = flask.request.get_json(silent=True)
    if not payload:
        return flask.jsonify({'status': 400, 'errors': 'Payload inválido ou em falta'}), 400

    used_at = payload.get('used_at')
    station_id = payload.get('station_id')

    if not used_at or not station_id:
        return flask.jsonify({'status': 400, 'errors': 'Campos used_at e station_id são obrigatórios'}), 400

    user_id = current_user['user_id']

    conn = db_connection()
    cur = conn.cursor()

    try:
        # 2. Verificar se o bilhete pertence ao cliente
        cur.execute("""
            SELECT id, estado, data_inicio_validade, data_fim_validade,
                   data_viagem, data_expiracao, tipo_bilhete_id_tipo, linha_id
            FROM bilhete
            WHERE id = %s AND cliente_pessoa_id = %s
        """, (ticket_id, user_id))
        bilhete = cur.fetchone()
        if not bilhete:
            return flask.jsonify({'status': 400, 'errors': 'Bilhete não encontrado ou não lhe pertence'}), 400

        estado = bilhete[1]
        inicio_validade = bilhete[2]
        fim_validade = bilhete[3]
        data_viagem = bilhete[4]
        data_expiracao = bilhete[5]
        tipo_bilhete_id = bilhete[6]
        bilhete_linha_id = bilhete[7]

        # 3. Verificar se o bilhete está ativo
        if estado != 'ativo':
            return flask.jsonify({'status': 400, 'errors': f'Bilhete com estado "{estado}" não pode ser usado'}), 400

        # 4. Validar a data/hora da validação em relação à validade do bilhete
        used_dt = datetime.datetime.strptime(used_at, '%Y-%m-%d %H:%M:%S')

        # Bilhete single_trip: deve ser usado na data_viagem exata
        if data_viagem is not None:
            if used_dt.date() != data_viagem:
                return flask.jsonify({'status': 400, 'errors': 'Bilhete single trip fora da data de viagem'}), 400

        # Bilhetes com intervalo de datas (daily, monthly)
        if inicio_validade and fim_validade:
            if used_dt.date() < inicio_validade or used_dt.date() > fim_validade:
                return flask.jsonify({'status': 400, 'errors': 'Bilhete fora do período de validade'}), 400

        # Se houver data_expiracao (campo genérico) – usado em passes?
        if data_expiracao and used_dt.date() > data_expiracao:
            return flask.jsonify({'status': 400, 'errors': 'Bilhete expirado'}), 400

        # 5. Para bilhetes single_trip, verificar se já foi usado
        if data_viagem is not None:
            cur.execute("SELECT COUNT(*) FROM validacao WHERE bilhete_id = %s", (ticket_id,))
            if cur.fetchone()[0] > 0:
                return flask.jsonify({'status': 400, 'errors': 'Bilhete single trip já foi usado'}), 400

        # 6. Verificar se o bilhete é válido para a linha da validação?
        #    A linha pode ser inferida a partir da paragem? Não directamente.
        #    Mas podemos obter a linha associada ao bilhete (se existir) e verificar se a paragem
        #    pertence a essa linha. Se bilhete_linha_id for NULL, é válido em qualquer linha.
        if bilhete_linha_id is not None:
            cur.execute("""
                SELECT 1 FROM trajeto
                WHERE linha_id = %s AND paragem_id = %s
                LIMIT 1
            """, (bilhete_linha_id, station_id))
            if not cur.fetchone():
                return flask.jsonify({'status': 400, 'errors': 'Esta paragem não pertence à linha do bilhete'}), 400

        # 7. Tentar encontrar uma viagem que corresponda à validação
        #    (opcional – se não encontrarmos, viagem_id fica NULL)
        viagem_id = None
        try:
            cur.execute("""
                SELECT v.id
                FROM viagem v
                JOIN trajeto t ON t.linha_id = v.linha_id
                WHERE t.paragem_id = %s
                  AND v.data_hora_partida <= %s
                  AND (v.data_hora_partida + (t.tempo_previsto_desde_origem || ' minutes')::INTERVAL) >= %s
                ORDER BY v.data_hora_partida DESC
                LIMIT 1
            """, (station_id, used_at, used_at))
            row = cur.fetchone()
            if row:
                viagem_id = row[0]
        except Exception:
            # Em caso de erro na inferência, mantemos NULL
            pass

        # 8. Inserir a validação
        cur.execute("""
            INSERT INTO validacao (data_hora, bilhete_id, viagem_id, paragem_id)
            VALUES (%s, %s, %s, %s)
        """, (used_at, ticket_id, viagem_id, station_id))

        # 9. Se for single_trip, marcar bilhete como 'usado'
        if data_viagem is not None:
            cur.execute("UPDATE bilhete SET estado = 'usado' WHERE id = %s", (ticket_id,))

        conn.commit()
        logger.debug(f'Bilhete {ticket_id} validado na paragem {station_id} às {used_at}')

        response = {'status': StatusCodes['success'], 'errors': None}

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        logger.error(f'POST /dbproj/ticket/use/{ticket_id} - erro: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)

##
## Endpoint 12 — Períodos de procura máxima e mínima (Admin only)
##
## Para cada linha, devolve a faixa horária com maior e a com menor
## número de validações (peak e low demand).
##
## Método: GET
## URL: http://localhost:8080/dbproj/report/demand
## Resposta: {"status": 200, "results": [ {"line_id": 1, "time_slot": "08:00-08:59", "validations": 1430}, ... ]}
##

@app.route('/dbproj/report/demand', methods=['GET'])
@token_required
def report_demand(current_user):
    logger.info('GET /dbproj/report/demand')

    # Apenas administradores podem aceder a relatórios
    if not current_user.get('is_admin'):
        return flask.jsonify({'status': 400, 'errors': 'Apenas administradores podem aceder a relatórios'}), 400

    conn = db_connection()
    cur = conn.cursor()

    try:
        query = """
            SELECT linha_id, time_slot, validations
            FROM (
                -- Subconsulta que agrupa as validações por linha e hora
                SELECT v.linha_id AS linha_id,
                       LPAD(EXTRACT(HOUR FROM va.data_hora)::text, 2, '0') || ':00-' ||
                       LPAD(EXTRACT(HOUR FROM va.data_hora)::text, 2, '0') || ':59' AS time_slot,
                       COUNT(*)::int AS validations
                FROM validacao va
                JOIN viagem v ON va.viagem_id = v.id
                GROUP BY v.linha_id, EXTRACT(HOUR FROM va.data_hora)
            ) sub
            WHERE (linha_id, validations) IN (
                -- Pico: maior número de validações por linha
                SELECT linha_id, MAX(validations)
                FROM (
                    SELECT v.linha_id,
                           COUNT(*)::int AS validations
                    FROM validacao va
                    JOIN viagem v ON va.viagem_id = v.id
                    GROUP BY v.linha_id, EXTRACT(HOUR FROM va.data_hora)
                ) peak_sub
                GROUP BY linha_id
            )
            UNION ALL
            SELECT linha_id, time_slot, validations
            FROM (
                SELECT v.linha_id AS linha_id,
                       LPAD(EXTRACT(HOUR FROM va.data_hora)::text, 2, '0') || ':00-' ||
                       LPAD(EXTRACT(HOUR FROM va.data_hora)::text, 2, '0') || ':59' AS time_slot,
                       COUNT(*)::int AS validations
                FROM validacao va
                JOIN viagem v ON va.viagem_id = v.id
                GROUP BY v.linha_id, EXTRACT(HOUR FROM va.data_hora)
            ) sub
            WHERE (linha_id, validations) IN (
                -- Baixa: menor número de validações por linha
                SELECT linha_id, MIN(validations)
                FROM (
                    SELECT v.linha_id,
                           COUNT(*)::int AS validations
                    FROM validacao va
                    JOIN viagem v ON va.viagem_id = v.id
                    GROUP BY v.linha_id, EXTRACT(HOUR FROM va.data_hora)
                ) low_sub
                GROUP BY linha_id
            )
            ORDER BY linha_id, validations DESC;
        """

        cur.execute(query)
        rows = cur.fetchall()

        results = []
        for row in rows:
            results.append({
                'line_id': int(row[0]),
                'time_slot': row[1],
                'validations': int(row[2])
            })

        response = {'status': StatusCodes['success'], 'errors': None, 'results': results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /dbproj/report/demand - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)

##
## Endpoint 13 — Top spenders por linha (Admin only)
##
## Para cada linha, devolve o(s) cliente(s) com maior gasto
## nos últimos 30 dias (soma do preço de compra dos bilhetes).
##
## Método: GET
## URL: http://localhost:8080/dbproj/report/top_spenders
## Resposta: {"status": 200, "results": [ {"line_id": 1, "customer_id": 17, "total_spent": 150.00}, ... ]}
##

@app.route('/dbproj/report/top_spenders', methods=['GET'])
@token_required
def report_top_spenders(current_user):
    logger.info('GET /dbproj/report/top_spenders')

    if not current_user.get('is_admin'):
        return flask.jsonify({'status': 400, 'errors': 'Apenas administradores podem aceder a relatórios'}), 400

    # Data limite: 30 dias atrás (passada como parâmetro para evitar funções SQL não lecionadas)
    thirty_days_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')

    conn = db_connection()
    cur = conn.cursor()

    try:
        query = """
            SELECT b.linha_id AS line_id,
                   b.cliente_pessoa_id AS customer_id,
                   SUM(b.preco_compra) AS total_spent
            FROM bilhete b
            WHERE b.linha_id IS NOT NULL
              AND b.data_compra >= %s
            GROUP BY b.linha_id, b.cliente_pessoa_id
            HAVING SUM(b.preco_compra) = (
                SELECT MAX(total)
                FROM (
                    SELECT SUM(b2.preco_compra) AS total
                    FROM bilhete b2
                    WHERE b2.linha_id = b.linha_id
                      AND b2.data_compra >= %s
                    GROUP BY b2.cliente_pessoa_id
                ) sub
            )
            ORDER BY b.linha_id;
        """

        cur.execute(query, (thirty_days_ago, thirty_days_ago))
        rows = cur.fetchall()

        results = []
        for row in rows:
            results.append({
                'line_id': int(row[0]),
                'customer_id': int(row[1]),
                'total_spent': round(float(row[2]), 2)
            })

        response = {'status': StatusCodes['success'], 'errors': None, 'results': results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /dbproj/report/top_spenders - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)

##
## Endpoint 14 — Relatório mensal (Admin only)
##
## Para cada linha e mês, apresenta o número de clientes que usaram
## o serviço pelo menos uma vez e quantos foram clientes repetidos (≥2 validações).
##
## Método: GET
## URL: http://localhost:8080/dbproj/report/monthly
## Resposta: {"status": 200, "results": [ {"line_id": 2, "month": 1, "active_customers": 1840, "repeat_customers": 620}, ... ]}
##

@app.route('/dbproj/report/monthly', methods=['GET'])
@token_required
def report_monthly(current_user):
    logger.info('GET /dbproj/report/monthly')

    if not current_user.get('is_admin'):
        return flask.jsonify({'status': 400, 'errors': 'Apenas administradores podem aceder a relatórios'}), 400

    conn = db_connection()
    cur = conn.cursor()

    try:
        query = """
            SELECT linha_id,
                   month,
                   COUNT(DISTINCT cliente_id) AS active_customers,
                   SUM(CASE WHEN validations >= 2 THEN 1 ELSE 0 END) AS repeat_customers
            FROM (
                -- Número de validações de cada cliente em cada linha/mês
                SELECT v.linha_id,
                       EXTRACT(MONTH FROM va.data_hora)::int AS month,
                       b.cliente_pessoa_id AS cliente_id,
                       COUNT(*)::int AS validations
                FROM validacao va
                JOIN viagem v ON va.viagem_id = v.id
                JOIN bilhete b ON va.bilhete_id = b.id
                GROUP BY v.linha_id, EXTRACT(MONTH FROM va.data_hora), b.cliente_pessoa_id
            ) sub
            GROUP BY linha_id, month
            ORDER BY linha_id, month;
        """

        cur.execute(query)
        rows = cur.fetchall()

        results = []
        for row in rows:
            results.append({
                'line_id': int(row[0]),
                'month': int(row[1]),
                'active_customers': int(row[2]),
                'repeat_customers': int(row[3])
            })

        response = {'status': StatusCodes['success'], 'errors': None, 'results': results}

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /dbproj/report/monthly - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}

    finally:
        if conn:
            conn.close()

    return flask.jsonify(response)


@app.route('/')
def landing_page():
    return """
    Metro Mondego API <br/>
    <br/>
    Endpoints disponíveis:<br/>
    PUT /dbproj/user — Autenticação (login)<br/>
    <br/>
    BD 2025-2026<br/>
    """


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.0 online: http://{host}:{port}')
