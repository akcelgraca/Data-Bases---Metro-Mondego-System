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
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            return flask.jsonify({'status': 400, 'errors': 'Token em falta'}), 400

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data
        except jwt.ExpiredSignatureError:
            return flask.jsonify({'status': 400, 'errors': 'Token expirado'}), 400
        except jwt.InvalidTokenError:
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
    payload = flask.request.get_json()

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