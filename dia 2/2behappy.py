import asyncio
import websockets

def is_happy_number(number):
    seen = set()
    while number != 1 and number not in seen:
        seen.add(number)
        number = sum(int(digit) ** 2 for digit in str(number))
    return number == 1

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
            print(f"Erro de conexão fechada: {e}")
            break
    return messages

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
            await websocket.send("start behappy")
            
            while True:
                # Recebe todas as respostas do servidor
                responses = await receive_all_messages(websocket)
                for response in responses:
                    print(f"Resposta do servidor: {response}")

                    # Verifica se o servidor está esperando uma resposta
                    if "Number:" in response:
                        number = int(response.split("Number:")[1].strip())
                        if is_happy_number(number):
                            await websocket.send("Feliz")
                            print("Resposta enviada: Feliz")
                        else:
                            await websocket.send("Infeliz")
                            print("Resposta enviada: Infeliz")

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Iniciar a execução da função connect
asyncio.run(connect())
