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
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        messages.append(message)
                    except asyncio.TimeoutError:
                        # Timeout para evitar espera infinita
                        break
                    except websockets.exceptions.ConnectionClosedOK:
                        print("Conexão encerrada de forma limpa.")
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
            await websocket.send("start source_control")  # Comando para iniciar o desafio "Conhecendo o Git"
            
            # Executa os comandos Git simulados
            git_commands = [
                "git add .",
                'git commit -m "docs: update README"',
                "git push"
            ]
            
            for command in git_commands:
                print(f"Enviando comando: {command}")
                await websocket.send(command)
                
                # Recebe todas as respostas após enviar o comando
                responses = await receive_all_messages()
                for response in responses:
                    print(f"Resposta do servidor: {response}")
                
            # Finaliza o loop se não houver mais mensagens
            print("Todos os comandos foram enviados e processados.")
            
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Iniciar a execução da função connect
asyncio.run(connect())
