import asyncio
import websockets
import traceback
import re

# Função para extrair os valores dos [*] Array


# Função para resolver 


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
            await websocket.send("start lost_treasure")
            
            while True:
                # Recebe todas as respostas do servidor
                responses = await receive_all_messages()
                for response in responses:
                    print(f"Resposta do servidor: {response}")

                    # Verifica se o servidor está solicitando a reposta
                    if "Príncipes:" in response and "Movimentos Mínimos Necessários:" in response:
                        # Extrai os valores para a resolução do problema
                        #princes, moves = extract_values(response)
                        #print(f"Príncipes: {princes}, Movimentos Mínimos Necessários: {moves}")

                        # Gera a lista de movimentos usando a função hanoi
                        #movements = hanoi(princes, 'A', 'C', 'B')
                        #print(movements)

                        # Converte a lista de movimentos para o formato solicitado e devolve ao servidor
                        #movements_str = str(movements).replace("'", '"')
                        await websocket.send()

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        traceback.print_exc()

# Iniciar a execução da função connect
asyncio.run(connect())
