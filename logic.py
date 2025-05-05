# logic.py (Versão 01/Mai)
import spacy
import random
import re
from datetime import datetime, date
from database import (
    get_current_players, get_next_match, get_player_info,
    get_coaches, get_random_trivia, get_quiz_questions,
    get_db_connection, get_preference, save_preference,
    get_last_match_result
)

# Carrega o modelo spaCy
try:
    nlp = spacy.load("pt_core_news_sm")
    print("Modelo spaCy 'pt_core_news_sm' carregado.")
except OSError:
    print("Execute: python -m spacy download pt_core_news_sm")
    nlp = None

# --- Funções de Geração de Resposta ---

def get_initial_message():
    """Retorna a mensagem de boas-vindas inicial do bot."""
    return "Sou o PanteraBot! 🐾 O que você quer saber sobre a FURIA hoje? Digite <em>ajuda</em> para ver algumas opções!"

def generate_greeting():
    """Gera uma saudação aleatória."""
    greetings = [
        "E aí, nação! 🐾 Manda a braba, o que você quer saber sobre a FURIA?",
        "Fala, torcedor(a)! Pronto(a) pra vibrar com a Pantera? Pergunta aí!",
        "Chega mais! Qual a boa sobre a FURIA que você quer hoje?",
        "Salve! PanteraBot na área. Em que posso ajudar?",
        "Oi! Preparado(a) pra aula de CS e paixão pela FURIA? Manda a pergunta!",
    ]
    return random.choice(greetings)

def generate_help_response():
    """Gera a mensagem de ajuda com exemplo de jogador randomizado."""
    example_player = "KSCERATO"
    try:
         players = get_current_players()
         if players:
             player_nicknames = [p['nickname'] for p in players]
             if player_nicknames:
                 example_player = random.choice(player_nicknames)
    except Exception as e:
         print(f"Erro ao buscar jogadores para exemplo de ajuda: {e}")

    capabilities = [
        "- Próximo jogo da FURIA",
        "- Jogadores atuais",
        "- Quem é o IGL",
        "- Quem é o Coach / Treinador",
        f"- Informações sobre um jogador (ex: quem é {example_player}?)",
        "- Curiosidade ou frase marcante (<em>/trivia</em>)",
        "- Um quiz sobre a FURIA (<em>/quiz</em>)",
        "- Resultado do último jogo"
    ]
    return "Sou o PanteraBot! 🐾 Você pode me perguntar sobre:\n\n" + "\n".join(capabilities)


def generate_player_list_response(session):
    """Gera lista de jogadores com intro variada, clarificação e exemplo randomizado."""
    players = get_current_players()
    if not players: return "Ih, parece que tô desatualizado sobre a line atual. Preciso verificar!"
    intros = ["A line atual da FURIA conta com essa galera braba:", "O time principal tá formado assim:", "Nossos representantes no servidor são estes monstros:", "Segura a line-up atual da Pantera:", "Quem tá defendendo nosso manto agora é:",]
    intro_line = random.choice(intros)
    clarification = "\n\n(Line-up Principal e Reservas Atuais)"
    player_lines = [f"- <strong>{p['nickname']}</strong> ({p['role']})" for p in players]
    example_player = "KSCERATO"
    player_nicknames = [p['nickname'] for p in players]
    if player_nicknames: example_player = random.choice(player_nicknames)
    response_base = intro_line + clarification + "\n" + "\n".join(player_lines)
    suggestion = f"\n\nQuer saber mais detalhes sobre algum deles? (Ex: 'quem é {example_player}?')"
    response = response_base + suggestion
    # Esta função não precisa modificar a session, apenas recebe se for chamada pelo 'sim'
    return response

# Recebe 'session' pois modifica o estado
def generate_next_match_response(session):
    """Gera informações sobre o próximo jogo com data dinâmica, variações e sugestão."""
    match = get_next_match()
    if not match:
        today = date.today(); formatted_today = today.strftime('%d/%m/%Y')
        no_match_responses = [f"Ainda não tenho data... (depois de {formatted_today})...", f"Segura a ansiedade!... (depois de {formatted_today})...", f"Calendário tá em branco... (depois de {formatted_today})...",]
        return random.choice(no_match_responses)
    tournament_comment = ""; opponent = match['opponent']; formatted_dt = match['formatted_datetime']
    if 'tournament' in match.keys() and match['tournament']:
        tournament_lower = match['tournament'].lower()
        if 'major' in tournament_lower: tournament_comment = "É MAJOR! 💥"
        else: tournament_comment = f"Valendo pelo <strong>{match['tournament']}</strong>!"
    else: tournament_comment = "Jogo importante!"
    intros = ["Prepare a torcida!...", "Anota aí!...", "É dia de FURIA!...", "Fica ligado!...",]
    outros = ["VAMO FURIA! 🖤", "Pra cima deles! #DIADEFURIA", "Contando as horas! ⏰", "Que vença o melhor...",]
    response_base = f"{random.choice(intros)} contra a <strong>{opponent}</strong> {tournament_comment} no dia <strong>{formatted_dt}</strong>."
    suggestion = f"\n\nQuer conferir a line-up atual?"
    response = response_base + suggestion + " " + random.choice(outros)
    session['state'] = 'awaiting_yes_no'; session['yes_no_action'] = 'get_players'; session['yes_no_subject'] = None; session.modified = True
    return response

# Recebe 'session' pois modifica o estado
def generate_player_info_response(nickname, session):
    """Gera informações sobre um jogador, incluindo stats, com sintaxe corrigida."""
    player = get_player_info(nickname)
    if not player:
        not_found_responses = [
            f"Hmm, não achei infos sobre <strong>{nickname}</strong>. O nick tá certo mesmo? 🤔",
            f"Será que <strong>{nickname}</strong> tá na nossa line? Não encontrei dados dele aqui.",
            f"Busquei aqui, mas nada sobre <strong>{nickname}</strong>. Confere se o nome é esse?",
            f"Não encontrei <strong>{nickname}</strong> na minha base de dados de jogadores atuais.",
            f"Sobre <strong>{nickname}</strong>... ainda não tenho essa informação. Tente outro jogador!",
            f"Minha busca por <strong>{nickname}</strong> voltou vazia. Tem certeza que é assim que escreve?",
        ]
        return random.choice(not_found_responses)

    # Formata data de entrada (MM/YYYY)
    formatted_join_date = player['join_date'] # Valor padrão
    try:
        if player['join_date']:
            join_date_obj = datetime.strptime(player['join_date'], '%Y-%m-%d')
            formatted_join_date = join_date_obj.strftime('%m/%Y')
    except Exception as e:
        # Mantém log de erro no console
        print(f"Erro formatar data {player['join_date'] if 'join_date' in player.keys() else 'N/A'} para {nickname}: {e}")

    # Variações para info básica
    player_role = player['role'] if 'role' in player.keys() else 'N/A'
    role_intros = [f"joga como <strong>{player_role}</strong>", f"atua na função de <strong>{player_role}</strong>", f"é o nosso <strong>{player_role}</strong>",]
    join_intros = [f"e entrou pra FURIA em {formatted_join_date}", f"e veste nossa camisa desde {formatted_join_date}", f"e faz parte da Pantera desde {formatted_join_date}",]
    compliments = ["Monstro!", "Craque!", "Representa!", "Orgulho!", "Lenda!"]
    player_name = player['name'] if 'name' in player.keys() else 'N/A'

    # Monta a parte inicial da resposta
    response_part1 = (f"O <strong>{player['nickname']}</strong> ({player_name}) "
                      f"{random.choice(role_intros)} "
                      f"{random.choice(join_intros)}. "
                      f"{random.choice(compliments)} 🔥")

    response_part2 = ""
    stats_found = []

    # Verifica e formata cada stat com try/except indentado corretamente
    if 'rating' in player.keys() and player['rating'] is not None:
        try:
            stats_found.append(f"Rating: {float(player['rating']):.2f}")
        except (ValueError, TypeError):
            pass

    if 'kd_ratio' in player.keys() and player['kd_ratio'] is not None:
        try:
            stats_found.append(f"K/D: {float(player['kd_ratio']):.2f}")
        except (ValueError, TypeError):
            pass

    if 'headshot_perc' in player.keys() and player['headshot_perc'] is not None:
        try:
            stats_found.append(f"HS: {float(player['headshot_perc']):.1f}%")
        except (ValueError, TypeError):
            pass

    if stats_found:
        stats_intros = ["Stats recentes:", "Desempenho (média):", "Números:", "Pra quem curte números:", "Algumas stats:",]
        stats_string = " | ".join(stats_found)
        response_part2 = f"\n\n📊 {random.choice(stats_intros)}\n{stats_string}"

    # Sugestão final
    suggestion = "\n\nQuer ver a line completa?"
    response = response_part1 + response_part2 + suggestion

    session['state'] = 'awaiting_yes_no'
    session['yes_no_action'] = 'get_players' # Ação se disser 'sim'
    session['yes_no_subject'] = None
    session.modified = True # Linha essencial para salvar o estado

    return response

# Não precisa de session
def generate_coach_response():
    """Busca os coaches no DB e gera uma resposta formatada com variações."""
    try: coaches = get_coaches()
    except Exception as e: print(f"Erro DB coaches: {e}"); return "Tive um problema ao buscar infos do coach."
    if not coaches: return "Ops! Sem info atualizada sobre o comando técnico agora."
    coach_names_formatted = []
    for c in coaches:
        name_part = f" ({c['name']})" if 'name' in c.keys() and c['name'] else ""
        coach_names_formatted.append(f"<strong>{c['nickname']}</strong>{name_part}")
    if len(coach_names_formatted) == 1: coach_list_str = coach_names_formatted[0]
    elif len(coach_names_formatted) == 2: coach_list_str = " e ".join(coach_names_formatted)
    else: coach_list_str = ", ".join(coach_names_formatted[:-1]) + " e " + coach_names_formatted[-1]
    responses = [f"A comissão técnica: {coach_list_str}.", f"No comando técnico: {coach_list_str}!", f"Quem orienta: {coach_list_str}.", f"Responsáveis pela estratégia: {coach_list_str}.",]
    return random.choice(responses)

# Não precisa de session
def generate_last_match_response():
    """Busca o último resultado e gera uma resposta formatada com variações."""
    try: last_match = get_last_match_result()
    except Exception as e: print(f"Erro DB último resultado: {e}"); return "Tive um problema ao buscar o último resultado."
    if not last_match:
        no_results = ["Ainda não tenho resultados anteriores.", "Não encontrei o último resultado...", "Busca pelo último jogo vazia...",]
        return random.choice(no_results)
    opponent = last_match['opponent']; tournament = last_match['tournament']; date_time = last_match['formatted_datetime']
    furia_score = last_match['furia_score']; opponent_score = last_match['opponent_score']
    score_str = ""; win_loss_comment = ""
    if furia_score is not None and opponent_score is not None:
        score_str = f"<strong>FURIA {furia_score} x {opponent_score} {opponent}</strong>"
        if furia_score > opponent_score: win_loss_comments = ["VITÓRIA!", "Ganhamos!", "GG WP!", "Amassamos!", "Deu bom!",]; win_loss_comment = f" ✅ {random.choice(win_loss_comments)}"
        elif furia_score < opponent_score: win_loss_comments = ["Que pena...", "Essa doeu.", "Bola pra frente.", "Fica pra próxima.", "Perdemos.",]; win_loss_comment = f" ❌ {random.choice(win_loss_comments)}"
        else: win_loss_comments = ["Empatamos.", "Jogo duro.", "Tudo igual."]; win_loss_comment = f" 🤝 {random.choice(win_loss_comments)}"
    else: score_str = f"contra <strong>{opponent}</strong>"; win_loss_comment = ". (Placar não registrado)"
    intros = ["No último confronto:", "O resultado mais recente foi:", "Olha só o último jogo:", "Relembrando a última partida:", "O último placar foi:",]
    tournament_str = f"pelo torneio <strong>{tournament}</strong>" if tournament else ""
    response = f"{random.choice(intros)}\n🗓️ Em {date_time},\n{score_str} {tournament_str}.{win_loss_comment}"
    return response

# Recebe 'session' pois modifica o estado
def generate_igl_response(session):
    """Gera a resposta sobre o IGL com variações, lógica corrigida e sugestão."""
    conn = get_db_connection(); igl_row = None; igl_nickname = None
    try:
        row_by_role = conn.execute("SELECT nickname FROM players WHERE lower(role) LIKE '%igl%'").fetchone()
        if row_by_role: igl_row = row_by_role
        else:
            row_by_fallback = conn.execute("SELECT nickname FROM players WHERE lower(nickname) = 'fallen'").fetchone()
            if row_by_fallback: igl_row = row_by_fallback
    except Exception as e: print(f"Erro DB IGL: {e}"); return "Tive um problema ao buscar info do IGL."
    finally: conn.close()
    if igl_row:
        igl_nickname = igl_row['nickname']
        intros = [f"Quem comanda a estratégia é <strong>{igl_nickname}</strong>!", f"A voz da experiência... <strong>{igl_nickname}</strong>.", f"No comando tático... <strong>{igl_nickname}</strong>!", f"O nosso IGL... <strong>{igl_nickname}</strong>.",]
        outros = ["Nosso capitão!", "Comanda muito!", "A mente por trás!", "Liderança pura!",]
        response_base = random.choice(intros) + " " + random.choice(outros)
        suggestion = f"\n\nQuer saber mais sobre o {igl_nickname}?"
        response = response_base + suggestion

        session['state'] = 'awaiting_yes_no'; 
        session['yes_no_action'] = 'get_player_info'; 
        session['yes_no_subject'] = igl_nickname; 
        session.modified = True
        
        return response
    else: 
        return "Opa, preciso confirmar quem tá de IGL no momento! A função pode variar."

# Não precisa de session
def generate_trivia_response():
    """Gera uma trivia/citação com variações na introdução e sugestão."""
    try: item = get_random_trivia()
    except Exception as e: print(f"Erro DB trivia: {e}"); return "Tive um problema ao buscar a trivia."
    if not item:
         no_trivia_responses = ["Deu branco aqui...", "Memória falhou...", "Não achei pérola...",]
         return random.choice(no_trivia_responses)
    response_base = ""
    if item['type'] == 'quote':
        quote_intros = ["Olha essa:", "Mandaram essa aqui:", "Pra refletir:", "Direto do KODE:", ]
        response_base = f"{random.choice(quote_intros)} <em>\"{item['content']}\"</em> - Dita por: <strong>{item['source']}</strong>."
    else:
         fact_intros = ["Você sabia? 🤔", "Fato curioso:", "Olha que interessante:", "Direto da enciclopédia:",]
         response_base = f"{random.choice(fact_intros)} {item['content']} (<strong>{item['source']}</strong>)."
    suggestion = f"\n\nQuer ouvir outra? Use o comando <em>/trivia</em>!"
    response = response_base + suggestion
    return response

# Não precisa de session
def generate_fallback_response():
    """Gera uma resposta padrão aleatória."""
    fallbacks = ["Essa aí me pegou!...", "Hmm, não captei...", "Xiii, buguei aqui....", "Desculpe, não processei...", "Ainda não aprendi...", "Minha bola de cristal...", "Essa foi um headshot...", "Não tenho essa info...", "Não entendi patavinas...", "Meu processador deu tela azul...",]
    return random.choice(fallbacks)

# --- Lógica do Quiz ---
# (Funções format_question, start_quiz, handle_quiz como estavam - minimizadas e limpas)
def format_question(question_data, index, total):
    option_a=str(question_data.get('option_a','')); option_b=str(question_data.get('option_b','')); option_c=str(question_data.get('option_c','')); question_text=str(question_data.get('question',''))
    return (f"--- <strong>Quiz Pergunta {index+1}/{total}</strong> ---\n\n<strong>{question_text}</strong>\n\nA) {option_a}\nB) {option_b}\nC) {option_c}\n\nResponda com A, B ou C.")
def start_quiz(session):
    num_questions_in_quiz = 3; questions = get_quiz_questions(num_questions=num_questions_in_quiz)
    if not questions or len(questions) < num_questions_in_quiz: return "Poxa, não consegui encontrar perguntas suficientes..."
    session['quiz_active']=True; session['quiz_questions']=[dict(q) for q in questions]; session['current_question_index']=0; session['quiz_score']=0; session.modified=True
    return format_question(session['quiz_questions'][0], 0, len(session['quiz_questions']))
def handle_quiz(session, user_answer):
    idx=session.get('current_question_index',0); questions=session.get('quiz_questions',[]); score=session.get('quiz_score',0)
    if not session.get('quiz_active') or not questions or idx >= len(questions): session['quiz_active']=False; session.modified=True; return "O quiz já acabou... Digite <em>/quiz</em>..."
    current_question=questions[idx]; correct_answer=current_question.get('correct_option','').upper(); explanation=current_question.get('explanation'); user_answer=user_answer.strip().upper(); feedback=""
    if user_answer == correct_answer: score+=1; session['quiz_score']=score; correct_feedback=["BOA! ✅", "É isso aí! ✅", "Mandou bem! ✅", "Na mosca! ✅",]; feedback=f"{random.choice(correct_feedback)}\n";
    elif user_answer in ['A', 'B', 'C']: wrong_feedback=[f"Ops! Correto: <strong>{correct_answer}</strong>. ❌", f"Quase! Correto: <strong>{correct_answer}</strong>. ❌", f"Não foi... Correto: <strong>{correct_answer}</strong>. ❌",]; feedback=f"{random.choice(wrong_feedback)}\n";
    else: return "Resposta inválida. Use A, B ou C."
    if explanation and (user_answer==correct_answer or user_answer in ['A','B','C']): feedback += f"<em>{explanation}</em>\n\n"
    next_idx=idx+1; session['current_question_index']=next_idx
    if next_idx >= len(questions):
        session['quiz_active']=False; final_header=f"<strong>Quiz finalizado!</strong>\n{score}/{len(questions)} acertos.\n"; final_comments_perfect=["Mandou bem demais! 🏆", "Gabaritou! 🏆", "Perfeito! 🏆",]; final_comments_good=["Foi bem! 👍", "Resultado sólido! 👍", "Legal! 👍",]; final_comments_bad=["Quase lá! 😉", "Faltou pouco! 😉", "Não desanime! 😉",]; final_message=final_header
        if score == len(questions): final_message += random.choice(final_comments_perfect)
        elif score >= len(questions)/2: final_message += random.choice(final_comments_good)
        else: final_message += random.choice(final_comments_bad)
        session.pop('quiz_questions', None); session.pop('current_question_index', None); session.pop('quiz_score', None); session.modified=True; return feedback+final_message
    else: next_question=questions[next_idx]; session.modified=True; return feedback+format_question(next_question, next_idx, len(questions))


# --- Processamento Principal da Mensagem ---

def process_message(user_message, session):
    """
    Analisa a mensagem do usuário, considerando estados e padrões,
    e retorna a resposta apropriada.
    """
    message_lower = user_message.lower().strip()
    session_id = session.get('session_id')

    if not session_id:
        print("!!! ERRO CRÍTICO: session_id não encontrado!") # Mantido log crítico
        return "Desculpe, ocorreu um erro com sua sessão. Tente recarregar a página."

    # Etapa 1: Verifica estados específicos ('awaiting_fav_player', 'awaiting_yes_no')
    current_state = session.get('state')
    if current_state == 'awaiting_fav_player':
        potential_player_name = user_message.strip(); players = get_current_players(); validated_player = None; player_nicknames_list = [p['nickname'] for p in players] if players else []
        if players:
            for p in players:
                if potential_player_name.lower() == p['nickname'].lower(): validated_player = p['nickname']; break
        if validated_player:
            save_preference(session_id, 'favorite_player', validated_player); session.pop('state', None); session.modified = True
            confirmations = [f"Show! Anotei... <strong>{validated_player}</strong>.", f"Entendido! <strong>{validated_player}</strong>...", f"Massa! Preferência... <strong>{validated_player}</strong>!",]
            return random.choice(confirmations)
        else:
            valid_names_str = ", ".join([f"<em>{n}</em>" for n in player_nicknames_list]) if player_nicknames_list else "Nenhum"
            error_message = f"Hmm, não reconheci '<strong>{potential_player_name}</strong>'... ({valid_names_str})..."
            session.pop('state', None); session.modified = True # Limpa estado mesmo com erro
            return error_message

    elif current_state == 'awaiting_yes_no':
        positive_responses = ['sim', 's', 'quero', 'pode', 'manda', 'claro', 'yes', 'y', 'uhum']
        action = session.get('yes_no_action'); subject = session.get('yes_no_subject')
        session.pop('state', None); session.pop('yes_no_action', None); session.pop('yes_no_subject', None); session.modified = True
        if message_lower in positive_responses:
            # Chamadas Corrigidas para passar 'session' onde necessário
            if action == 'get_player_info' and subject: return generate_player_info_response(subject, session)
            elif action == 'get_players': return generate_player_list_response(session)
            else: print(f"[DEBUG] Invalid action/subject for yes/no state: {action}, {subject}") # Mantido log útil
        # Se não for 'sim', deixa continuar para processamento normal abaixo...

    # --- Etapa 2: Processamento normal ---
    bot_response = None; ask_preference_question = False

    # 2a: Comandos/Padrões de Alta Prioridade
    if message_lower == 'ajuda' or message_lower == '/ajuda': bot_response = generate_help_response()
    elif message_lower in ["bom dia", "boa tarde", "boa noite"]: bot_response = generate_greeting()
    elif message_lower == '/quiz': bot_response = start_quiz(session)
    elif message_lower == '/trivia': bot_response = generate_trivia_response()
    elif "coach" in message_lower or "treinador" in message_lower: bot_response = generate_coach_response()
    elif "quem é o igl" in message_lower or "capitao" in message_lower: bot_response = generate_igl_response(session) # Passa session
    elif "último jogo" in message_lower or "resultado" in message_lower: bot_response = generate_last_match_response()
    elif re.match(r"(?:quem é|fale sobre|infos sobre)\s+(.+)", user_message, re.IGNORECASE):
        match_info = re.match(r"(?:quem é|fale sobre|infos sobre)\s+(.+)", user_message, re.IGNORECASE)
        potential_nickname = match_info.group(1).strip()
        if potential_nickname.lower() not in ['o igl', 'o coach', 'o treinador']:
             bot_response = generate_player_info_response(potential_nickname, session) # Passa session
        elif potential_nickname.lower() == 'o igl': bot_response = generate_igl_response(session) # Passa session
        elif potential_nickname.lower() in ['o coach', 'o treinador']: bot_response = generate_coach_response()
        else: bot_response = generate_player_info_response(potential_nickname, session) # Passa session
    elif session.get('quiz_active'): bot_response = handle_quiz(session, user_answer=user_message)

    # 2b: NLP Genérico (se nada acima funcionou)
    if bot_response is None:
        intent = None; entities = {'player_nickname': None}
        if nlp:
            doc = nlp(user_message)
            # Listas de Keywords (mantidas)
            greetings_kw = ["oi", "ola", "eae", "salve", "opa"]
            schedule_kw = ["jogo", "joga", "partida", "quando", "próximo", "agenda", "calendário"]
            players_kw = ["jogadores", "time", "lineup", "line", "quem", "squad", "elenco"]
            igl_kw = ["igl", "capitao", "capitão", "lider", "líder", "estrategia", "tatico", "comando"]
            coach_kw = ["coach", "treinador", "técnico", "tecnico"]
            last_match_kw = ["último", "ultimo", "resultado", "placar", "ganhou", "perdeu", "anterior"]
            trivia_kw = ["frase", "historia", "fatos", "sabia"]
            try:
                current_players_list = get_current_players()
                known_players_db = [p['nickname'].lower() for p in current_players_list] if current_players_list else []
            except Exception as e: print(f"Erro NLP DB: {e}"); known_players_db = [] # Mantido log de erro

            # Detecção de Intenção NLP
            for token in doc:
                lemma = token.lemma_.lower(); text_lower = token.text.lower()
                if not intent:
                    if text_lower in greetings_kw or lemma in greetings_kw: intent = 'greeting'
                    elif text_lower in schedule_kw or lemma in schedule_kw: intent = 'get_schedule'
                    elif text_lower in players_kw or lemma in players_kw: intent = 'get_players'
                    elif text_lower in igl_kw or lemma in igl_kw: intent = 'get_igl'
                    elif text_lower in coach_kw or lemma in coach_kw: intent = 'get_coach'
                    elif text_lower in last_match_kw or lemma in last_match_kw: intent = 'get_last_result'
                    elif lemma in trivia_kw: intent = 'get_trivia'
                # Detecção de Entidade NLP
                if text_lower in known_players_db or lemma in known_players_db:
                    entities['player_nickname'] = token.text
                    if intent is None or intent == 'get_players': intent = 'get_player_info'
            if not intent and entities['player_nickname']: intent = 'get_player_info'
            # print(f"Debug NLP -> Intenção: {intent}, Entidades: {entities}") # Removido

            # Mapeamento Intenção NLP -> Resposta
            if intent == 'greeting': bot_response = generate_greeting()
            elif intent == 'get_schedule': bot_response = generate_next_match_response(session) # Passa session
            elif intent == 'get_players':
                bot_response = generate_player_list_response(session) # Passa session
                if bot_response and 'desatualizado' not in bot_response:
                    fav_player = get_preference(session_id, 'favorite_player')
                    if fav_player is None and not session.get('asked_fav_player'): ask_preference_question = True
            elif intent == 'get_igl': bot_response = generate_igl_response(session) # Passa session
            elif intent == 'get_coach': bot_response = generate_coach_response()
            elif intent == 'get_last_result': bot_response = generate_last_match_response()
            elif intent == 'get_trivia': bot_response = generate_trivia_response()
            elif intent == 'get_player_info' and entities['player_nickname']:
                 bot_response = generate_player_info_response(entities['player_nickname'], session) # Passa session

        # Fallback final
        if bot_response is None:
            # print("[DEBUG] Nenhuma intenção reconhecida. Usando fallback geral.") # Removido
            bot_response = generate_fallback_response()

    # --- Etapa 3: Adiciona pergunta sobre preferência ---
    if ask_preference_question:
        fav_player_check = get_preference(session_id, 'favorite_player')
        if fav_player_check is None:
            question_text = "\n\nA propósito, quem é seu jogador favorito da line atual?"
            bot_response = str(bot_response) + question_text
            session['state'] = 'awaiting_fav_player'; session['asked_fav_player'] = True; session.modified = True
            # print(f"[DEBUG] Perguntando jogador favorito. Set state for {session_id}") # Removido
        # else: print(f"[DEBUG] Ia perguntar fav_player, mas já definido: {fav_player_check}.") # Removido

    # --- Etapa 4: Retorna a resposta final ---
    return bot_response if bot_response is not None else generate_fallback_response()


# (if __name__ == '__main__': ...) # Bloco de teste local mantido comentado