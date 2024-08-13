import asyncio
import websockets
import re

async def receive_message(websocket):
    try:
        message = await websocket.recv()
        print(f"Recebido: {message}")  # Adiciona depuração para verificar a mensagem recebida
        return message.strip()  # Remove espaços adicionais
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Erro de conexão fechada: {e}")
        return None

def extract_array_and_target(messages):
    print("Entrando em extract_array_and_target")  # Depuração
    combined_message = "\n".join(messages)
    array_match = re.search(r'\[\*\] Array: \[(.*?)\]', combined_message)
    target_match = re.search(r'\[\*\] Target: (\d+)', combined_message)
    
    if array_match and target_match:
        array = list(map(int, array_match.group(1).split(',')))
        target = int(target_match.group(1))
        print(f"Array extraído: {array}, Target extraído: {target}")  # Depuração
        return array, target
    print("Saindo de extract_array_and_target sem encontrar array ou target")  # Depuração
    return None, None

async def connect():
    uri = "wss://ctf-challenges.devops.hotmart.com/echo"
    try:
        async with websockets.connect(uri) as websocket:
            print("Conectado ao servidor WebSocket.")
            
            # Recebe todas as mensagens iniciais do servidor
            while True:
                message = await receive_message(websocket)
                if message is None:
                    break
                print(f"Resposta do servidor:\n{message}")
                if "Use o comando" in message:
                    break
            
            # Envia o comando inicial para começar o desafio
            print("Enviando comando 'start search'...")
            await websocket.send("start search")
            print("Comando 'start search' enviado.")

            # Acumula mensagens até termos o array e o target
            accumulated_messages = []

            while True:
                print("Aguardando resposta do servidor...")  # Depuração
                response = await receive_message(websocket)
                if response is None:
                    print("Nenhuma resposta recebida após enviar 'start search'.")
                    break
                
                print(f"Resposta do servidor: {response}")
                accumulated_messages.append(response)

                # Extrai o array e o alvo da resposta se tivermos todas as informações necessárias
                if len(accumulated_messages) >= 2:
                    array, target = extract_array_and_target(accumulated_messages)
                    if array is not None and target is not None:
                        # Encontra o índice do alvo no array
                        try:
                            print("Procurando índice do alvo no array...")  # Depuração
                            index = array.index(target)
                            print(f"Índice encontrado: {index}")
                            
                            # Envia o índice de volta ao servidor (somente o número)
                            await websocket.send(str(index))
                            print(f"Índice enviado: {index}")
                            
                            # Verifica a resposta do servidor
                            response_confirmation = await receive_message(websocket)
                            if response_confirmation is None:
                                print("Nenhuma resposta recebida após enviar o índice.")
                                break
                            print(f"Resposta do servidor após envio: {response_confirmation}")
                            
                        except ValueError:
                            print("Alvo não encontrado no array.")
                            await websocket.send("not found")
                            print("Resposta 'not found' enviada ao servidor.")
                        
                        # Limpa as mensagens acumuladas para a próxima rodada
                        accumulated_messages = []

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        import traceback
        traceback.print_exc()

# Iniciar a execução da função connect
asyncio.run(connect())
