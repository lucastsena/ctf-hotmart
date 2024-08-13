import asyncio
import websockets
import re
import base64
import hashlib

# Função para decodificar uma string codificada em base64
def decode_base64(encoded_str):
    return base64.b64decode(encoded_str).decode('utf-8')

# Função para gerar o hash MD5 de uma sentença
def generate_md5(sentence):
    return hashlib.md5(sentence.encode('utf-8')).hexdigest()

# Função para gerar o hash SHA1 de uma sentença
def generate_sha1(sentence):
    return hashlib.sha1(sentence.encode('utf-8')).hexdigest()

# Função para decodificar uma string codificada em ROT13
def decode_rot13(encoded_str):
    return encoded_str.translate(str.maketrans(
        "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
        "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm"))

# Função para decodificar uma string codificada em binário
def decode_binary(encoded_str):
    binary_values = [encoded_str[i:i+7] for i in range(0, len(encoded_str), 7)]
    decoded_str = ''.join([chr(int(bv, 2)) for bv in binary_values])
    return decoded_str

# Função para decodificar uma string codificada em hexadecimal
def decode_hex(encoded_str):
    return bytes.fromhex(encoded_str).decode('utf-8')

# Função para decodificar uma string codificada com XOR de um único byte
def decode_single_byte_xor(encoded_str, key):
    try:
        print(f"Decodificando XOR: string={encoded_str}, key={key}")
        decoded_bytes = base64.b64decode(encoded_str)  # Decodifica a string base64
        return ''.join(chr(byte ^ key) for byte in decoded_bytes)  # Aplica XOR e converte para string
    except Exception as e:
        print(f"Erro durante a decodificação XOR: {e}")
        return Non

# Função assíncrona para conectar ao servidor WebSocket
async def connect():
    uri = "wss://ctf-challenges.devops.hotmart.com/echo"
    try:
        async with websockets.connect(uri) as websocket:
            print("Conectado ao servidor WebSocket.")

            async def receive_all_messages():
                messages = []
                while True:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                        messages.append(message)
                    except asyncio.TimeoutError:
                        break
                    except websockets.exceptions.ConnectionClosedOK:
                        break
                    except websockets.exceptions.ConnectionClosedError as e:
                        print(f"Erro de conexão fechada: {e}")
                        break
                return messages

            initial_messages = await receive_all_messages()
            for message in initial_messages:
                print(f"Resposta do servidor:\n{message}")

            await websocket.send("start cryptomix")

            accumulated_response = ""
            while True:
                responses = await receive_all_messages()
                for response in responses:
                    print(f"Resposta do servidor: {response}")
                    accumulated_response += response

                    if "================================================================================" in accumulated_response:
                        method_match = re.search(r"Method:\s*(\w+(-\d+)?)", accumulated_response, re.IGNORECASE)
                        encoded_match = re.search(r"Encoded:\s*([\w=]+)", accumulated_response, re.IGNORECASE)
                        sentence_match = re.search(r"Sentence:\s*([\w_]+)", accumulated_response, re.IGNORECASE)
                        key_match = re.search(r"Key:\s*(0x[\da-fA-F]+)", accumulated_response, re.IGNORECASE)

                        if method_match:
                            method = method_match.group(1)
                            print(f"Método encontrado: {method}")

                        if encoded_match:
                            encoded_str = encoded_match.group(1)
                            print(f"String codificada encontrada: {encoded_str}")
                        elif sentence_match:
                            encoded_str = sentence_match.group(1)
                            print(f"Sentença encontrada: {encoded_str}")
                        else:
                            accumulated_response = ""
                            continue

                        if key_match:
                            key = int(key_match.group(1), 16)
                            print(f"Chave encontrada: {key}")
                        else:
                            key = None

                        try:
                            print(f"Iniciando decodificação com método: {method}")
                            if method == "base64":
                                decoded_str = decode_base64(encoded_str)
                            elif method == "md5":
                                decoded_str = generate_md5(encoded_str)
                            elif method == "sha1":
                                decoded_str = generate_sha1(encoded_str)
                            elif method == "rot-13":
                                decoded_str = decode_rot13(encoded_str)
                            elif method == "binary":
                                decoded_str = decode_binary(encoded_str)
                            elif method == "hex":
                                decoded_str = decode_hex(encoded_str)
                            elif method == "single_byte_xor" and key is not None:
                                decoded_str = decode_single_byte_xor(encoded_str, key)
                                if decoded_str is None:
                                    raise ValueError("Erro de decodificação XOR")
                                print(f"Resposta bruta do single_byte_xor: '{decoded_str}'")
                            else:
                                decoded_str = "_".join(encoded_str.split())
                        except Exception as e:
                            print(f"Erro durante a decodificação: {e}")
                            accumulated_response = ""
                            continue

                        decoded_str = decoded_str.strip()
                        print(f"Tipo da resposta: {type(decoded_str)}")
                        print(f"Resposta final: {decoded_str}")
                        await websocket.send(decoded_str)

                        accumulated_response = ""

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Iniciar a execução da função connect
asyncio.run(connect())
