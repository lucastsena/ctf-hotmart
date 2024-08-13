import asyncio
import websockets
from collections import deque

# Lista para armazenar os caracteres coletados
caracteres_coletados = []

async def solve_challenge():
    uri = "wss://ctf-challenges.devops.hotmart.com/echo"
    
    async with websockets.connect(uri) as websocket:
        await websocket.send("start spy")
        print("Comando enviado: start spy")

        while True:
            response = await websocket.recv()
            
            if "Bem-Vindo ao HotCTF" in response:
                continue
            
            print(f"Mensagem recebida: {response}")
            
            if "invalid command" in response.lower():
                print("Comando inválido. Verifique o comando enviado.")
                break
            
            if "[*] Sucesso!" in response:
                # Extrai o caractere da mensagem de sucesso
                caractere = response.split("[")[-1].split("]")[0]
                caracteres_coletados.append(caractere)
                print(f"Caractere coletado: {caractere}")
                print(f"Lista de caracteres coletados: {caracteres_coletados}")
            
            if "[*] Mapa" in response:
                # Captura o mapa do desafio
                mapa = response.splitlines()[1:]  # Pegando o mapa excluindo as linhas desnecessárias
                mapa = [list(linha) for linha in mapa]

                # Analisa o mapa usando a nova lógica
                comando, matriz_convertida, matriz_de_risco = analisar_novo_mapa(mapa)

                # Exibe as matrizes convertida e de risco
                print("Matriz Convertida:")
                for linha in matriz_convertida:
                    print("".join(linha))

                print("\nMatriz de Risco:")
                for linha in matriz_de_risco:
                    print("".join(map(str, linha)))

                # Envia o comando ao servidor
                await websocket.send(comando)
                print(f"Comando enviado ao servidor: {comando}")

def converter_mapa(mapa):
    conversao = {
        '🥷': 'A',  # Loid
        '💻': 'T',  # Terminal
        '🏠': 'C',  # Casa
        '^': '^',   # Guarda olhando para cima
        'v': 'v',   # Guarda olhando para baixo
        '<': '<',   # Guarda olhando para a esquerda
        '>': '>',   # Guarda olhando para a direita
        '_': '_'    # Espaço vazio
    }
    matriz_convertida = [[conversao[char] for char in linha] for linha in mapa]
    return matriz_convertida

def gerar_matriz_de_risco(mapa_convertido):
    linhas = len(mapa_convertido)
    colunas = len(mapa_convertido[0])
    risco = [[0] * colunas for _ in range(linhas)]
    
    direcoes = {
        '^': (-1, 0),
        'v': (1, 0),
        '<': (0, -1),
        '>': (0, 1)
    }
    
    for y, linha in enumerate(mapa_convertido):
        for x, char in enumerate(linha):
            if char in ['C', '^', 'v', '<', '>']:  # Casas e guardas são áreas de risco
                risco[y][x] = 1
                if char in direcoes:
                    dy, dx = direcoes[char]
                    ny, nx = y + dy, x + dx
                    while 0 <= ny < linhas and 0 <= nx < colunas:
                        if mapa_convertido[ny][nx] == 'C':  # Casas bloqueiam a visão
                            break
                        risco[ny][nx] = 1
                        if mapa_convertido[ny][nx] in ['_', 'T']:  # Continue até um obstáculo ou borda
                            ny += dy
                            nx += dx
                        else:
                            break
    return risco


def encontrar_posicoes(mapa_convertido):
    loid_position = None
    terminal_position = None
    
    for y, linha in enumerate(mapa_convertido):
        for x, char in enumerate(linha):
            if char == 'A':
                loid_position = (y, x)
            elif char == 'T':
                terminal_position = (y, x)
    
    return loid_position, terminal_position

def verificar_caminho_seguro(matriz_de_risco, loid_position, terminal_position):
    filas = deque([loid_position])
    visitados = set([loid_position])
    
    while filas:
        y, x = filas.popleft()
        
        if (y, x) == terminal_position:
            return True
        
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            
            if 0 <= ny < len(matriz_de_risco) and 0 <= nx < len(matriz_de_risco[0]) and (ny, nx) not in visitados and matriz_de_risco[ny][nx] == 0:
                visitados.add((ny, nx))
                filas.append((ny, nx))
    
    return False

def analisar_novo_mapa(mapa):
    matriz_convertida = converter_mapa(mapa)
    matriz_de_risco = gerar_matriz_de_risco(matriz_convertida)
    
    # Encontrar posição de Loid e do terminal
    loid_position, terminal_position = encontrar_posicoes(matriz_convertida)
    
    # Checar se Loid ou o terminal estão em áreas de risco
    if matriz_de_risco[loid_position[0]][loid_position[1]] == 1 or matriz_de_risco[terminal_position[0]][terminal_position[1]] == 1:
        return "Espere!", matriz_convertida, matriz_de_risco
    
    # Verificar se existe um caminho seguro entre Loid e o terminal
    if verificar_caminho_seguro(matriz_de_risco, loid_position, terminal_position):
        return "Vai!", matriz_convertida, matriz_de_risco
    else:
        return "Espere!", matriz_convertida, matriz_de_risco

# Executar o desafio
asyncio.run(solve_challenge())

# Ao final, imprimir a lista completa de caracteres coletados
print("Caracteres coletados ao final do desafio:", "".join(caracteres_coletados))
