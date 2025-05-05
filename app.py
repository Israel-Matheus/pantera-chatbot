# app.py (Versão 01/Mai)
import logic
import os
import uuid
import random
from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta
from logic import process_message
from database import init_db, get_preference

# --- Inicialização do Aplicativo Flask ---
app = Flask(__name__)

# --- Configuração da Sessão ---
# Use uma chave secreta forte em produção!
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
app.permanent_session_lifetime = timedelta(hours=1)

# --- Inicialização do Banco de Dados ---
print("Inicializando o banco de dados (se necessário)...")
init_db()
print("Banco de dados pronto.")

# --- Definição das Rotas ---

@app.route("/")
def index():
    """Renderiza a página inicial, garante session_id e passa preferência para template."""
    # print("\n--- [DEBUG] Acessando Rota '/' ---") # Removido
    session_id = session.get('session_id')
    is_new_session = False

    # Garante session_id
    if not session_id:
        is_new_session = True
        new_id = str(uuid.uuid4())
        session['session_id'] = new_id
        session_id = new_id
        # print(f"[DEBUG] Novo session_id gerado: {session_id}") # Removido
    # else:
        # print(f"[DEBUG] session_id existente encontrado: {session_id}") # Removido

    # Busca preferência
    fav_player = get_preference(session_id, 'favorite_player')
    # print(f"[DEBUG] Jogador favorito buscado para {session_id}: {fav_player}") # Removido

    # Inicializa histórico SOMENTE se não existir, com saudação PADRÃO
    if 'chat_history' not in session:
        # print("[DEBUG] Histórico NÃO encontrado na sessão. Inicializando...") # Removido
        session['chat_history'] = []
        initial_greeting = "Sou o PanteraBot! 🐾 O que você quer saber sobre a FURIA hoje? Digite <em>ajuda</em> para ver algumas opções!"
        session['chat_history'].append({"sender": "bot", "text": initial_greeting})
        # print(f"[DEBUG] Saudação PADRÃO adicionada ao histórico.") # Removido
    # else:
        # print("[DEBUG] Histórico JÁ EXISTE na sessão.") # Removido

    session.permanent = True
    if is_new_session or 'chat_history' not in session: # Marca se algo realmente mudou
         session.modified = True

    history_to_render = session.get('chat_history', [])
    # print(f"[DEBUG] Histórico a ser enviado: {len(history_to_render)} itens") # Removido
    # print(f"[DEBUG] Jogador favorito a ser enviado: {fav_player}") # Removido
    # print("--- [DEBUG] Renderizando index.html ---") # Removido
    return render_template("index.html",
                           chat_history=history_to_render,
                           favorite_player=fav_player) # Passa a variável para o HTML

@app.route("/chat", methods=["POST"])
def chat():
    """Recebe a mensagem do usuário via JSON, processa e retorna a resposta do chatbot."""
    try:
        user_message = request.json["message"]
        # print(f"Mensagem recebida: {user_message}") # Removido

        # Manipulação segura do histórico
        current_history = session.get('chat_history', [])
        current_history.append({"sender": "user", "text": user_message})

        # Chama a lógica do bot
        bot_response = process_message(user_message, session)

        # Adiciona a resposta do bot à lista
        current_history.append({"sender": "bot", "text": bot_response})

        # Atualiza a sessão
        session['chat_history'] = current_history
        session.modified = True

        # Limita o tamanho do histórico
        max_history_per_user = 50
        if len(session['chat_history']) > max_history_per_user:
             session['chat_history'] = session['chat_history'][-max_history_per_user:]
             # session.modified = True # Já foi marcado acima

        # print(f"Resposta do bot: {bot_response}") # Removido
        # print(f"Estado da sessão após processar: {dict(session)}") # Removido
        return jsonify({"response": bot_response})

    except Exception as e:
        import traceback
        # Mantém log de erro no console do servidor
        print(f"!!! Erro no endpoint /chat ({type(e).__name__}): {e}")
        traceback.print_exc()
        # Retorna uma mensagem de erro genérica para o usuário
        return jsonify({"response": "Ocorreu um erro interno no servidor. Tente novamente."}), 500

# --- Execução do Servidor ---
if __name__ == "__main__":
    # Mantenha debug=True apenas durante o desenvolvimento
    print("Iniciando servidor Flask...")
    app.run(host='0.0.0.0', port=5000, debug=True) # Mantenha debug=True por enquanto
