import asyncio
import websockets
import traceback

# Função para encontrar a soma máxima de um subarray contínuo usando o Algoritmo de Kadane
def max_subarray_sum(arr):
    max_so_far = arr[0]
    max_ending_here = arr[0]
    
    for i in range(1, len(arr)):
        max_ending_here = max(arr[i], max_ending_here + arr[i])
        max_so_far = max(max_so_far, max_ending_here)
    
    return max_so_far

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

                    # Verifica se o servidor está solicitando a soma máxima de um subarray contínuo
                    if "Array:" in response:
                        # Extrai o array da resposta do servidor
                        array_str = response.split("Array: ")[1].strip("[]\n")
                        array = list(map(int, array_str.split(", ")))
                        print(f"Array recebido: {array}")

                        # Calcula a soma máxima do subarray contínuo usando o Algoritmo de Kadane
                        max_sum = max_subarray_sum(array)
                        print(f"Soma máxima do subarray contínuo: {max_sum}")

                        # Envia a resposta ao servidor
                        await websocket.send(str(max_sum))

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        traceback.print_exc()

# Iniciar a execução da função connect
asyncio.run(connect())
