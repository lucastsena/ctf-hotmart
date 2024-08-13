import asyncio
import websockets

async def connect():
    uri = "wss://ctf-challenges.devops.hotmart.com/echo"
    try:
        async with websockets.connect(uri) as websocket:
            print("Conectado ao servidor WebSocket.")
            
            # Função para receber todas as mensagens do servidor com timeout
            async def receive_all_messages():
                messages = []
                while True:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                        messages.append(message)
                    except asyncio.TimeoutError:
                        break
                    except websockets.exceptions.ConnectionClosedOK:
                        break
                    except websockets.exceptions.ConnectionClosedError as e:
                        print(f"Erro de conexão fechada: {e}")
                        break
                return messages

            # Função para encontrar o maior palíndromo em uma palavra
            def find_largest_palindrome(word):
                max_palindrome = ""
                for i in range(len(word)):
                    for j in range(i + 1, len(word) + 1):
                        substring = word[i:j]
                        if len(substring) > 1 and substring == substring[::-1] and len(substring) > len(max_palindrome):
                            max_palindrome = substring
                return max_palindrome if max_palindrome else "Sem palindromo"

            # Recebe todas as mensagens iniciais do servidor
            initial_messages = await receive_all_messages()
            for message in initial_messages:
                print(f"Resposta do servidor:\n{message}")
            
            # Envia o comando inicial para começar o desafio
            await websocket.send("start palindromo")
            
            while True:
                # Recebe todas as respostas do servidor
                responses = await receive_all_messages()
                for response in responses:
                    print(f"Resposta do servidor: {response}")

                    # Verifica se o servidor está pedindo para encontrar um palíndromo
                    if "Word:" in response:
                        word = response.split("Word: ")[1].strip()
                        largest_palindrome = find_largest_palindrome(word)
                        print(f"Enviando resposta: {largest_palindrome}")  # Imprime a resposta no console
                        await websocket.send(largest_palindrome)

                # Verifica se o comando não foi reconhecido e repete se necessário
                if any("🙀 invalid command" in response for response in responses):
                    print("Comando inválido. Por favor, tente novamente.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Iniciar a execução da função connect
asyncio.run(connect())
