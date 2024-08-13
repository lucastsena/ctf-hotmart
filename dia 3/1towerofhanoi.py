import asyncio
import websockets
import traceback
import re

# Função para extrair os valores dos príncipes e movimentos necessários
def extract_values(server_response):
    princes_pattern = re.compile(r"Príncipes: \[(\d+)\]")
    moves_pattern = re.compile(r"Movimentos Mínimos Necessários: \[(\d+)\]")

    princes_match = princes_pattern.search(server_response)
    moves_match = moves_pattern.search(server_response)

    if princes_match and moves_match:
        princes = int(princes_match.group(1))
        moves = int(moves_match.group(1))
        return princes, moves
    else:
        raise ValueError("Não foi possível extrair os valores dos príncipes e movimentos necessários.")

# Função para resolver a Torre de Hanói
def hanoi(n, source, target, auxiliary):
    if n == 1:
        return [(source, target)]
    else:
        return hanoi(n-1, source, auxiliary, target) + [(source, target)] + hanoi(n-1, auxiliary, target, source)

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
            await websocket.send("start towerofhanoi")
            
            while True:
                # Recebe todas as respostas do servidor
                responses = await receive_all_messages()
                for response in responses:
                    print(f"Resposta do servidor: {response}")

                    # Verifica se o servidor está solicitando uma nova lista
                    if "Príncipes:" in response and "Movimentos Mínimos Necessários:" in response:
                        # Extrai os valores dos príncipes e movimentos necessários
                        princes, moves = extract_values(response)
                        print(f"Príncipes: {princes}, Movimentos Mínimos Necessários: {moves}")

                        # Gera a lista de movimentos usando a função hanoi
                        movements = hanoi(princes, 'A', 'C', 'B')
                        print(movements)

                        # Converte a lista de movimentos para o formato solicitado
                        movements_str = str(movements).replace("'", '"')
                        await websocket.send(movements_str)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        traceback.print_exc()

# Iniciar a execução da função connect
asyncio.run(connect())
