# database.py (Versão 01/Mai)
import sqlite3
import os
import random
from datetime import datetime

# Nome do arquivo do banco de dados
DATABASE_FILE = 'chatbot_data.db'

def get_db_connection():
    """Cria ou conecta ao banco de dados"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DATABASE_FILE)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Retorna linhas como dicionários
    return conn

def init_db(force_recreate=False):
    """
    Inicializa o banco de dados com tabelas e dados iniciais se não existir
    ou se force_recreate for True.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, DATABASE_FILE)
    if force_recreate and os.path.exists(db_path):
        print("Forçando recriação do banco de dados...")
        os.remove(db_path)

    print(f"Conectando ao banco de dados: {db_path}")
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Verificando/Criando tabelas...")

    # Tabela de Jogadores (com Stats)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, nickname TEXT NOT NULL UNIQUE, role TEXT, join_date TEXT,
            rating REAL DEFAULT NULL, kd_ratio REAL DEFAULT NULL, headshot_perc REAL DEFAULT NULL
        )
    ''')
    if cursor.execute("SELECT COUNT(*) FROM players").fetchone()[0] == 0:
        print("Populando tabela 'players' com stats...")
        players_data = [
            # ('Nome', 'Nick', 'Role', 'Entrada', Rating, KD, HS%)
            ('Gabriel Toledo', 'FalleN', 'AWP/IGL', '2023-07-03', 1.05, 1.10, 45.5),
            ('Kaike Cerato', 'KSCERATO', 'Rifler/Lurker', '2018-02-05', 1.20, 1.25, 50.2),
            ('Yuri Santos', 'yuurih', 'Rifler/Entry', '2017-11-15', 1.15, 1.18, 55.1),
            ('Mareks Gaļinskis', 'YEKINDAR', 'Rifler/Entry', '2025-04-22', 1.05, 1.08, 52.0),
            ('Danil Golubenko', 'molodoy', 'Rifler', '2025-04-01', 1.21, 1.20, 49.0),
            ('Marcelo Cespedes', 'chelo', 'Reserva', '2022-08-22', 1.08, 1.05, 58.3),
            ('Felipe Medeiros', 'skullz', 'Reserva', '2024-07-18', 1.04, 1.00, 47.0),

            # Comissão Técnica
            ('Marcos Especimel', 'sidde', 'Coach', '2024-03-01', None, None, None),
            ('Aitor Fernandez', 'Hepa', 'Coach', '2024-03-01', None, None, None),
        ]
        cursor.executemany(
            'INSERT INTO players (name, nickname, role, join_date, rating, kd_ratio, headshot_perc) VALUES (?, ?, ?, ?, ?, ?, ?)',
            players_data)
    print("Tabela 'players' verificada/criada.")

    # Tabela de Próximos Jogos (com resultado)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT, opponent TEXT NOT NULL, tournament TEXT,
            match_datetime TEXT NOT NULL, status TEXT DEFAULT 'scheduled',
            furia_score INTEGER DEFAULT NULL, opponent_score INTEGER DEFAULT NULL
        )
    ''')
    if cursor.execute("SELECT COUNT(*) FROM schedule").fetchone()[0] == 0:
        print("Populando tabela 'schedule' com exemplos...")
        schedule_data = [
            ('The MongolZ', 'PGL Budapest 2025', '2025-04-09 09:50', 'completed', 0, 2),
            # Adicione um jogo futuro se quiser testar get_next_match
            # ('Exemplo Rival Futuro', 'Campeonato Exemplo', '2025-12-31 23:59', 'scheduled', None, None),
        ]
        cursor.executemany(
             'INSERT INTO schedule (opponent, tournament, match_datetime, status, furia_score, opponent_score) VALUES (?, ?, ?, ?, ?, ?)',
             schedule_data)
    print("Tabela 'schedule' verificada/criada.")

    # Tabela de Curiosidades/Frases
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trivia (
            id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL,
            content TEXT NOT NULL, source TEXT
        )
    ''')
    if cursor.execute("SELECT COUNT(*) FROM trivia").fetchone()[0] == 0:
        print("Populando tabela 'trivia'...")
        trivia_data = [
            ('quote', 'Vamo pra cima!', 'Guerri (Coach)'), ('quote', 'Tem que respeitar a pantera!', 'Torcida'),
            ('curiosity', 'A FURIA foi fundada em 2017.', 'História'), ('curiosity', 'O KSCERATO é conhecido por sua mira consistente.', 'Gameplay'),
            ('curiosity', 'A Pantera do logo da FURIA...', 'Branding'), ('quote', 'A torcida é o nosso sexto jogador!', 'FalleN'),
            ('curiosity', 'A Gaming House da FURIA nos EUA fica na Flórida.', 'Estrutura'), ('quote', 'Confia no processo!', 'Comunidade')
        ]
        cursor.executemany('INSERT INTO trivia (type, content, source) VALUES (?, ?, ?)', trivia_data)
    print("Tabela 'trivia' verificada/criada.")

    # Tabela de Quizzes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT NOT NULL, option_a TEXT NOT NULL,
            option_b TEXT NOT NULL, option_c TEXT NOT NULL, correct_option TEXT NOT NULL, explanation TEXT
        )
    ''')
    if cursor.execute("SELECT COUNT(*) FROM quizzes").fetchone()[0] == 0:
        print("Populando tabela 'quizzes'...")
        quiz_data = [
             ('Qual jogador é conhecido como "Professor"?', 'KSCERATO', 'FalleN', 'yuurih', 'B', 'FalleN...'),
             ('Em que ano a FURIA foi fundada?', '2015', '2017', '2019', 'B', 'A FURIA...'),
             ('Qual destes mapas é historicamente um dos mais fortes da FURIA?', 'Dust 2', 'Inferno', 'Mirage', 'C', 'Mirage...'),
             ('Quem foi o coach da FURIA por um longo período...?', 'guerri', 'tacitus', 'peacemaker', 'A', 'Nicholas "guerri"...'),
             ('Qual a cor predominante no logo da FURIA?', 'Vermelho', 'Preto', 'Verde', 'B', 'O logo...'),
             ('Contra qual time a FURIA jogou sua primeira partida em um Major...?', 'Astralis', 'Natus Vincere', 'Team Liquid', 'B', 'A estreia...')
         ]
        cursor.executemany('INSERT INTO quizzes (question, option_a, option_b, option_c, correct_option, explanation) VALUES (?, ?, ?, ?, ?, ?)', quiz_data)
    print("Tabela 'quizzes' verificada/criada.")

    # Tabela 'user_preferences'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL, preference_key TEXT NOT NULL,
            preference_value TEXT NOT NULL, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, preference_key)
        )
    ''')
    print("Tabela 'user_preferences' verificada/criada.")

    conn.commit()
    conn.close()
    print("Banco de dados verificado/inicializado com sucesso.")

# --- Funções de Acesso aos Dados ---

def get_current_players():
    """Busca JOGADORES atuais (inclui Reservas, exclui Coaches/Staff)."""
    conn = get_db_connection()
    players = conn.execute("SELECT nickname, role FROM players WHERE role IS NULL OR lower(role) NOT LIKE '%coach%' ORDER BY nickname").fetchall()
    conn.close()
    return players

def get_coaches():
    """Busca os coaches e assistant coaches atuais."""
    conn = get_db_connection()
    coaches = conn.execute("SELECT name, nickname FROM players WHERE lower(role) LIKE '%coach%' ORDER BY nickname").fetchall()
    conn.close()
    return coaches

def get_next_match():
    current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    # print(f"Buscando jogos após: {current_time_str}") # Debug Removido
    conn = get_db_connection()
    match = conn.execute("SELECT opponent, tournament, strftime('%d/%m às %H:%M', match_datetime) as formatted_datetime FROM schedule WHERE status = 'scheduled' AND match_datetime > ? ORDER BY match_datetime ASC LIMIT 1", (current_time_str,)).fetchone()
    conn.close()
    return match

def get_last_match_result():
    """Busca o resultado do último jogo completado."""
    current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db_connection()
    result = None
    try:
        cursor = conn.execute("SELECT opponent, tournament, strftime('%d/%m/%Y às %H:%M', match_datetime) as formatted_datetime, furia_score, opponent_score FROM schedule WHERE status = 'completed' AND match_datetime < ? ORDER BY match_datetime DESC LIMIT 1", (current_time_str,))
        result = cursor.fetchone()
    except sqlite3.Error as e: print(f"Erro DB get_last_match_result: {e}")
    finally: conn.close()
    # print(f"[DEBUG DB] Último resultado buscado: {dict(result) if result else 'Nenhum encontrado'}") # Debug Removido
    return result

def get_player_info(nickname):
    """Busca informações completas de um jogador, INCLUINDO STATS."""
    conn = get_db_connection()
    player = conn.execute('SELECT name, nickname, role, join_date, rating, kd_ratio, headshot_perc FROM players WHERE lower(nickname) = ?', (nickname.lower(),)).fetchone()
    conn.close()
    return player

def get_random_trivia():
    conn = get_db_connection()
    item = conn.execute('SELECT type, content, source FROM trivia ORDER BY RANDOM() LIMIT 1').fetchone()
    conn.close()
    return item

def get_quiz_questions(num_questions=3):
    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM quizzes ORDER BY RANDOM() LIMIT ?', (num_questions,)).fetchall()
    conn.close()
    return [dict(q) for q in questions] if questions else []

# --- Funções de Preferências ---

def save_preference(session_id, key, value):
    """Salva ou atualiza uma preferência para um session_id específico."""
    if not session_id or not key or value is None: print(f"Erro ao salvar preferência: dados inválidos..."); return
    conn = get_db_connection()
    try:
        conn.execute('INSERT OR REPLACE INTO user_preferences (session_id, preference_key, preference_value, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)', (str(session_id), str(key), str(value)))
        conn.commit()
        # print(f"Preferência salva: session_id={session_id}, key={key}, value={value}") # Debug Removido
    except sqlite3.Error as e: print(f"Erro ao salvar preferência no DB: {e}")
    finally: conn.close()

def get_preference(session_id, key):
    """Busca o valor de uma preferência para um session_id específico."""
    if not session_id or not key: print(f"Erro ao buscar preferência: dados inválidos..."); return None
    conn = get_db_connection()
    preference_value = None
    try:
        cursor = conn.execute('SELECT preference_value FROM user_preferences WHERE session_id = ? AND preference_key = ?', (str(session_id), str(key)))
        result = cursor.fetchone()
        if result: preference_value = result['preference_value'] # ; print(f"Preferência encontrada: ... value={preference_value}") # Debug Removido
        # else: print(f"Preferência NÃO encontrada: session_id={session_id}, key={key}") # Debug Removido
    except sqlite3.Error as e: print(f"Erro ao buscar preferência no DB: {e}")
    finally: conn.close()
    return preference_value

# --- Bloco Principal ---
if __name__ == '__main__':
    print("Executando inicialização do banco de dados...")
    # init_db(force_recreate=True) # Descomente para forçar
    init_db()
    print("Execução de inicialização concluída.")
