import asyncio
import websockets
import re
from itertools import combinations

async def receive_all_messages(websocket):
    messages = []
    while True:
        try:
            message = await asyncio.wait_for(websocket.recv(), timeout=0.5)  # Timeout aumentado para garantir a recepção
            messages.append(message)
        except asyncio.TimeoutError:
            break
        except websockets.exceptions.ConnectionClosed:
            break
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Erro de conexão fechada: {e}")
            break
    return messages

def extract_heroes_and_ability(response):
    heroes_match = re.search(r'\[\*] Hérois: \[(.*?)\]', response)
    ability_match = re.search(r'Habilidade: (\d+)', response)
    
    if heroes_match and ability_match:
        heroes = list(map(int, heroes_match.group(1).split(',')))
        ability = int(ability_match.group(1))
        return heroes, ability
    return None, None

def find_heroes_indices(heroes, ability):
    for combo in combinations(range(len(heroes)), 3):
        if sum(heroes[i] for i in combo) == ability:
            return combo
    return None

async def connect():
    uri = "wss://ctf-challenges.devops.hotmart.com/echo"
    try:
        async with websockets.connect(uri) as websocket:
            print("Conectado ao servidor WebSocket.")
            
            # Recebe todas as mensagens iniciais do servidor
            initial_messages = await receive_all_messages(websocket)
            for message in initial_messages:
                print(f"Resposta do servidor:\n{message}")
            
            # Envia o comando inicial para começar o desafio
            await websocket.send("start rpg")
            
            while True:
                # Recebe todas as respostas do servidor
                responses = await receive_all_messages(websocket)
                for response in responses:
                    print(f"Resposta do servidor: {response}")

                    # Extrai os heróis e a habilidade da resposta
                    heroes, ability = extract_heroes_and_ability(response)
                    if heroes and ability:
                        # Encontra os índices dos heróis
                        indices = find_heroes_indices(heroes, ability)
                        if indices:
                            response_indices = '[' + ','.join(map(str, indices)) + ']'
                            total_ability = sum(heroes[i] for i in indices)
                            print(f"Índices escolhidos: {response_indices}")
                            print(f"Total de habilidade: {total_ability}")

                            # Envia os índices dos heróis
                            try:
                                await websocket.send(response_indices)
                                print(f"Enviado: {response_indices}")
                                
                                # Verifica se a resposta foi recebida corretamente
                                response_confirmation = await websocket.recv()
                                print(f"Resposta do servidor após envio: {response_confirmation}")
                                
                            except Exception as e:
                                print(f"Erro ao enviar a resposta: {e}")
                        
                    # Verifica se o servidor está esperando uma resposta
                    if "Informe o ID dos hérois" in response:
                        heroes, ability = extract_heroes_and_ability(response)
                        if heroes and ability:
                            indices = find_heroes_indices(heroes, ability)
                            if indices:
                                response_indices = '[' + ','.join(map(str, indices)) + ']'
                                try:
                                    # Adiciona um pequeno atraso antes de reenviar a resposta
                                    await asyncio.sleep(1)
                                    await websocket.send(response_indices)
                                    print(f"Enviado novamente: {response_indices}")
                                except Exception as e:
                                    print(f"Erro ao reenviar a resposta: {e}")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Iniciar a execução da função connect
asyncio.run(connect())
