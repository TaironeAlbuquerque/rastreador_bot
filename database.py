import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('rastreador.db')
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            cpf TEXT UNIQUE,
            nome TEXT,
            data_cadastro TEXT
        )
        ''')
        
        # Tabela de pedidos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            codigo_rastreio TEXT PRIMARY KEY,
            user_id INTEGER,
            descricao TEXT,
            status TEXT,
            ultima_atualizacao TEXT,
            FOREIGN KEY (user_id) REFERENCES usuarios (user_id)
        )
        ''')
        
        conn.commit()

def adicionar_usuario(user_id, cpf, nome):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO usuarios (user_id, cpf, nome, data_cadastro)
        VALUES (?, ?, ?, datetime('now'))
        ''', (user_id, cpf, nome))
        conn.commit()

def adicionar_pedido(user_id, codigo_rastreio, descricao):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO pedidos (codigo_rastreio, user_id, descricao, status, ultima_atualizacao)
        VALUES (?, ?, ?, 'Pendente', datetime('now'))
        ''', (codigo_rastreio, user_id, descricao))
        conn.commit()

def buscar_pedidos_por_cpf(cpf):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT p.codigo_rastreio, p.descricao, p.status, p.ultima_atualizacao
        FROM pedidos p
        JOIN usuarios u ON p.user_id = u.user_id
        WHERE u.cpf = ?
        ''', (cpf,))
        return cursor.fetchall()

def atualizar_status_pedido(codigo_rastreio, novo_status):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE pedidos
        SET status = ?, ultima_atualizacao = datetime('now')
        WHERE codigo_rastreio = ?
        ''', (novo_status, codigo_rastreio))
        conn.commit()

def buscar_usuario_por_cpf(cpf):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE cpf = ?', (cpf,))
        return cursor.fetchone()
