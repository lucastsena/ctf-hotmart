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

            # Função para calcular o número de inversões em um array
            def count_inversions(array):
                inversions = 0
                for i in range(len(array)):
                    for j in range(i + 1, len(array)):
                        if array[i] > array[j]:
                            inversions += 1
                return inversions

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

                # Verifica se o servidor está pedindo o número de inversões
                while any("Array:" in response for response in responses):
                    for response in responses:
                        if "Array:" in response:
                            array_str = response.split("Array: ")[1].split("]")[0] + "]"
                            array = eval(array_str)
                            inversions = count_inversions(array)
                            await websocket.send(str(inversions))
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
