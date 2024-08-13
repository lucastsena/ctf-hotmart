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
                        message = await asyncio.wait_for(websocket.recv(), timeout=5)
                        messages.append(message)
                    except asyncio.TimeoutError:
                        break
                    except websockets.exceptions.ConnectionClosedOK:
                        break
                    except websockets.exceptions.ConnectionClosedError as e:
                        print(f"Erro de conexão fechada: {e}")
                        break
                return messages

            # Função para calcular o próximo número na sequência de Fibonacci
            def next_fibonacci(seq):
                return seq[-1] + seq[-2]

            # Recebe todas as mensagens iniciais do servidor
            initial_messages = await receive_all_messages()
            for message in initial_messages:
                print(f"Resposta do servidor:\n{message}")
            
            while True:
                comando = input("Digite o comando (ou 'exit' para sair): ")

                if comando.lower() == 'exit':
                    print("Encerrando a conexão.")
                    break

                # Envia o comando para o servidor
                await websocket.send(comando)
                
                # Recebe todas as respostas do servidor
                responses = await receive_all_messages()
                for response in responses:
                    print(f"Resposta do servidor: {response}")

                # Verifica se o servidor está pedindo o próximo número de Fibonacci
                while any("Entre com o proximo elemento da sequencia:" in response for response in responses):
                    for response in responses:
                        if "Sequencia Fibonacci:" in response:
                            seq_str = response.split("Sequencia Fibonacci: ")[1].split("]")[0] + "]"
                            seq = eval(seq_str)
                            next_fib = next_fibonacci(seq)
                            await websocket.send(str(next_fib))
                            responses = await receive_all_messages()
                            for response in responses:
                                print(f"Resposta do servidor: {response}")

                # Verifica se o comando não foi reconhecido e repete se necessário
                if any("🙀 invalid command" in response for response in responses):
                    print("Comando inválido. Por favor, tente novamente.")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        raise e

# Iniciar a execução da função connect
asyncio.run(connect())
