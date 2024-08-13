import asyncio
import websockets
import heapq
import logging

logging.basicConfig(level=logging.INFO)

async def receive_all_messages(websocket):
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
            logging.error(f"Erro de conexão fechada: {e}")
            break
    return messages

def dijkstra(graph, start, end):
    queue = [(0, start)]
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    visited = set()

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == end:
            return current_distance

        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))

    return float('inf')

async def connect():
    uri = "wss://ctf-challenges.devops.hotmart.com/echo"
    try:
        async with websockets.connect(uri) as websocket:
            logging.info("Conectado ao servidor WebSocket.")

            # Recebe todas as mensagens iniciais do servidor
            initial_messages = await receive_all_messages(websocket)
            for message in initial_messages:
                logging.info(f"Resposta do servidor:\n{message}")

            # Envia o comando inicial para começar o desafio
            await websocket.send("start uailog")

            while True:
                # Recebe todas as respostas do servidor
                responses = await receive_all_messages(websocket)
                for response in responses:
                    logging.info(f"Resposta do servidor: {response}")

                # Filtra as mensagens relevantes
                try:
                    ruas_response = next(resp for resp in responses if "[*] Ruas:" in resp)
                    ponto_inicial_response = next(resp for resp in responses if "[*] Ponto de Entrega Inicial:" in resp)
                    ponto_final_response = next(resp for resp in responses if "[*] Ponto de Entrega Final:" in resp)

                    # Processa as mensagens relevantes
                    if ruas_response and ponto_inicial_response and ponto_final_response:
                        ruas_str = ruas_response.split("[*] Ruas: ")[1]
                        ruas = eval(ruas_str)

                        ponto_inicial = ponto_inicial_response.split("[*] Ponto de Entrega Inicial: ")[1].strip()
                        ponto_final = ponto_final_response.split("[*] Ponto de Entrega Final: ")[1].strip()

                        # Constrói o grafo
                        graph = {}
                        for rua in ruas:
                            if rua[0] not in graph:
                                graph[rua[0]] = []
                            if rua[1] not in graph:
                                graph[rua[1]] = []
                            graph[rua[0]].append((rua[1], rua[2]))
                            graph[rua[1]].append((rua[0], rua[2]))

                        # Calcula a menor distância usando Dijkstra
                        menor_distancia = dijkstra(graph, ponto_inicial, ponto_final)
                        await websocket.send(str(menor_distancia))

                except StopIteration:
                    continue
                except Exception as e:
                    logging.error(f"Erro ao processar os dados: {e}")
                    continue

    except Exception as e:
        logging.error(f"Ocorreu um erro: {e}")

# Iniciar a execução da função connect
asyncio.run(connect())
