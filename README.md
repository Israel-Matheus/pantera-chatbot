# PanteraBot: Chatbot Interativo da FURIA

**(Projeto Experiência Conversacional)**

## Descrição

> *Desenvolvi este chatbot web interativo utilizando Python (Flask) e JavaScript como parte do Challenge "Experiência Conversacional". O objetivo é oferecer aos fãs da FURIA Esports uma forma prática e engajadora de obter informações atualizadas sobre o time de CS, como line-up, agenda, resultados, além de interagir com quizzes e trivias. O projeto utiliza processamento básico de linguagem natural (spaCy) e armazena dados em SQLite, buscando oferecer uma experiência de usuário fluida e informativa.*

## Funcionalidades Principais

* Consulta de line-up atual (jogadores principais e reservas).
* Informações detalhadas sobre jogadores específicos (incluindo estatísticas básicas como Rating, K/D, HS%).
* Informações sobre o IGL e a Comissão Técnica (Coach/Assistant Coach).
* Agenda do próximo jogo agendado.
* Resultado da última partida completada (com placar e comentário).
* Quiz interativo sobre a FURIA com perguntas aleatórias.
* Trivia com curiosidades e frases marcantes sobre a organização/jogadores.
* Comando de ajuda (`ajuda` ou `/ajuda`) listando as capacidades.
* Saudação inicial personalizada para usuários recorrentes (baseada no jogador favorito salvo na sessão).
* Sugestões contextuais para guiar a conversa.
* Respostas com variações para uma interação mais natural.
* Reconhecimento de diferentes formas de saudação.

## Tecnologias Utilizadas

* **Backend:** Python 3, Flask
* **Banco de Dados:** SQLite 3
* **NLP:** spaCy (modelo `pt_core_news_sm`)
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
* **Comunicação Frontend-Backend:** Fetch API (Assíncrona, JSON)
* **Gerenciamento de Sessão:** Flask Session
* **Outros:** uuid (para IDs de sessão), re (Expressões Regulares)

## Estrutura do Projeto

```
pantera-chatbot/
│
├── .gitignore         # Arquivos/pastas ignorados pelo Git
├── app.py             # Aplicação Flask principal, rotas HTTP (/ e /chat)
├── database.py        # Módulo para interação com o DB (conexão, init, funções CRUD)
├── logic.py           # Módulo com a lógica do chatbot e processamento de mensagens
├── requirements.txt   # Lista de dependências Python
├── static/            # Pasta para arquivos estáticos
│   ├── css/
│   │   └── style.css  # Estilos CSS
│   └── js/
│       └── chat.js    # Lógica JavaScript do frontend
└── templates/         # Pasta para templates HTML (Flask/Jinja2)
    └── index.html     # Estrutura HTML da página do chat

# Nota: O arquivo chatbot_data.db é criado na primeira execução e ignorado pelo .gitignore
```

## Configuração e Instalação

Siga os passos abaixo para configurar e rodar o projeto localmente:

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/Israel-Matheus/pantera-chatbot.git](https://github.com/Israel-Matheus/pantera-chatbot.git)
    cd pantera-chatbot
    ```
2.  **Crie e Ative um Ambiente Virtual:** (Recomendado)
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux / macOS
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Baixe o Modelo spaCy:** (Necessário apenas na primeira vez)
    ```bash
    python -m spacy download pt_core_news_sm
    ```
5.  **Inicialize o Banco de Dados:** (Cria o arquivo `chatbot_data.db` com tabelas e dados iniciais)
    * *Opcional:* Se o arquivo `chatbot_data.db` já existir, delete-o antes se quiser começar com dados limpos.
    ```bash
    python database.py
    ```

## Como Rodar

1.  **Inicie o Servidor Flask:** (Certifique-se que seu ambiente virtual está ativado)
    ```bash
    python app.py
    ```
2.  **Acesse no Navegador:** Abra seu navegador e vá para o endereço que aparecer no console.

## Exemplos de Uso

Você pode interagir com o PanteraBot perguntando sobre:

* `oi` / `salve` / `bom dia`
* `ajuda`
* `jogadores atuais` / `line up`
* `quem é o coach?` / `treinador`
* `quem é o igl?`
* `quem é FalleN?` / `infos sobre KSCERATO`
* `próximo jogo`
* `último jogo` / `resultado`
* `/trivia`
* `/quiz` (e depois respondendo A, B ou C)

## Autor

* **Israel Matheus**

## Licença

> Distribuído sob a Licença MIT. Veja `LICENSE.md` para mais informações.
