// Espera o DOM carregar completamente antes de executar o script
document.addEventListener('DOMContentLoaded', () => {

    // Seleciona os elementos do DOM
    const chatOutput = document.getElementById('chat-output');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Função para adicionar mensagem ao chat output
    function displayMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');

        const messageParagraph = document.createElement('p');
        messageParagraph.innerHTML = text;
        messageDiv.appendChild(messageParagraph);

        chatOutput.appendChild(messageDiv);

        // Rola automaticamente para a última mensagem
        chatOutput.scrollTop = chatOutput.scrollHeight;
    }

    // Função para simular a resposta do bot (Placeholder)
    function getBotResponse(userText) {
        // Lógica simples de resposta (pode ser expandida)
        const lowerCaseText = userText.toLowerCase();

        if (lowerCaseText.includes('olá') || lowerCaseText.includes('oi')) {
            return 'Olá! Tudo bem?';
        } else if (lowerCaseText.includes('ajuda')) {
            return 'Claro, como posso ajudar?';
        } else if (lowerCaseText.includes('furia')) {
            return 'FURIA é uma grande organização de e-sports! #DIADEFURIA';
        } else {
            return `Você disse: "${userText}". Ainda estou aprendendo!`; // Resposta padrão
        }
    }

// Função para enviar a mensagem do usuário E buscar resposta do backend
async function sendMessage() { // Adicionado 'async' para poder usar 'await'
    const userText = userInput.value.trim();

    if (userText !== '') {
        displayMessage(userText, 'user'); // Mostra a mensagem do usuário imediatamente
        userInput.value = ''; // Limpa o campo de input

        // --- Início da Modificação ---
        try {
            // Envia a mensagem para o backend Flask na rota /chat
            const response = await fetch('/chat', { // 'await' espera a resposta do fetch
                method: 'POST', // Método HTTP
                headers: {
                    'Content-Type': 'application/json' // Informa que está enviando JSON
                },
                body: JSON.stringify({ message: userText }) // Converte o objeto JS em string JSON
            });

            if (!response.ok) {
                // Se a resposta do servidor não for OK (ex: erro 500)
                throw new Error(`Erro do servidor: ${response.status}`);
            }

            const data = await response.json(); // Pega a resposta JSON do backend

            // Verifica se a resposta contém a chave 'reply' esperada
            if (data && data.response) {
                // Simula um pequeno atraso antes de exibir a resposta do bot (opcional)
                setTimeout(() => {
                    displayMessage(data.response, 'bot'); // Exibe a resposta vinda do backend
                }, 300); // Atraso de 300ms
            } else {
                 displayMessage("Desculpe, não recebi uma resposta válida do servidor.", "bot");
            }

        } catch (error) {
            // Se ocorrer um erro na comunicação (rede, servidor fora, etc.)
            console.error('Erro ao enviar mensagem:', error);
            displayMessage("Erro ao conectar com o servidor. Tente novamente mais tarde.", "bot");
        }
        // --- Fim da Modificação ---
    }
}

    // Event listener para o botão de enviar
    sendButton.addEventListener('click', sendMessage);

    // Event listener para a tecla Enter no campo de input
    userInput.addEventListener('keypress', (event) => {
        // Verifica se a tecla pressionada foi Enter (código 13)
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // displayMessage("Olá! Como posso ajudar hoje?", "bot");

     console.log("Chatbot inicializado com estilo Furia!");

}); // Fim do DOMContentLoaded