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
    if not payload or 'username' not in payload or 'password' not in payload:
        return flask.jsonify({'status': 400, 'errors': 'Username e password são obrigatórios'}), 400
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
        # Numa versão de produção, usaríamos bcrypt ou argon2 para comparar hashes seguros.
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

        cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM pessoa")
        new_id = cur.fetchone()[0]

        statement = '''
            INSERT INTO pessoa (id, nome, email, username, password_hash)
            VALUES (%s, %s, %s, %s, %s)
        '''
        cur.execute(statement, (new_id, name, email, username, password_hash))

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

        # Gerar novo ID (simulação de auto-incremento)
        cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM pessoa")
        new_id = cur.fetchone()[0]

        # Inserir em pessoa
        statement = '''
            INSERT INTO pessoa (id, nome, email, username, password_hash)
            VALUES (%s, %s, %s, %s, %s)
        '''
        cur.execute(statement, (new_id, name, email, username, password_hash))

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
