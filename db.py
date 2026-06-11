import mysql.connector
from mysql.connector import Error, pooling
import os
# Configurações de conexão com o banco de dados
_DB_PARAMS = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'igreja_membros',
    'charset': 'utf8mb4',
    'use_pure': True,
    'connection_timeout': 10,
    'autocommit': False,
}

_pool = None

# Criando pool de conexões
def criar_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name='igreja_pool',
            pool_size=5,
            pool_reset_session=True,
            **_DB_PARAMS
        )

# Get connection entra no pool e não conecta diretamente ao banco, isso melhora a performance e evita sobrecarga de conexões
def get_connection():
    try:
        if _pool is None:
            criar_pool()
        return _pool.get_connection()
    except Error as e:
        raise Exception(f'Não foi possível obter conexão do pool: {e}')

# Função genérica para executar queries, com tratamento de erros
def execute_query(sql, params=None, fetch=False):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        if fetch:
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.rowcount
    except Error as e:
        conn.rollback()
        raise Exception(f'Erro ao executar query: {e}')
    finally:
        cursor.close()
        conn.close()

# Função para executar uma query e retornar um único resultado
def execute_one(sql, params=None):
    resultados = execute_query(sql, params, fetch=True)
    return resultados[0] if resultados else None

# Nessa função, tentamos conectar ao usando o dados informados anteriormente, e executamos o script SQL para criar o banco e as tabelas. Se ocorrer algum erro, ele é capturado e exibido.
def iniciar_bd():
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password=''
        )
        cursor = conn.cursor()
        arquivo_sql = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(arquivo_sql, 'r', encoding='utf-8') as f:
            script_sql = f.read()
        for stmt in script_sql.split(';'):
            stmt = stmt.strip()
            if stmt:
                cursor.execute(stmt)
        conn.commit()
        cursor.close()
        conn.close()
        print('Banco e tabelas inicializados com sucesso!')
    except Exception as e:
        print(f'Erro ao inicializar o banco: {e}')
