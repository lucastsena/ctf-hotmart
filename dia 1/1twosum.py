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
            
            # Recebe todas as mensagens iniciais do servidor
            initial_messages = await receive_all_messages()
            for message in initial_messages:
                print(f"Resposta do servidor:\n{message}")
            
            # Envia o comando inicial para começar o desafio
            await websocket.send("start organizer")
            
            while True:
                # Recebe todas as respostas do servidor
                responses = await receive_all_messages()
                for response in responses:
                    print(f"Resposta do servidor: {response}")

                # Verifica se o servidor está solicitando uma nova lista
                if any("Entre com a nova lista:" in response for response in responses):
                    # Extrai a lista de inteiros da resposta do servidor
                    for response in responses:
                        if "Lista:" in response:
                            lista_str = response.split("Lista: ")[1].strip()
                            lista = eval(lista_str)  # Converte a string para uma lista Python
                            break
                    
                    # Reorganiza a lista com pares antes dos ímpares
                    lista_pares = [x for x in lista if x % 2 == 0]
                    lista_impares = [x for x in lista if x % 2 != 0]
                    nova_lista = lista_pares + lista_impares
                    
                    # Envia a nova lista para o servidor
                    await websocket.send(str(nova_lista))

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Iniciar a execução da função connect
asyncio.run(connect())
