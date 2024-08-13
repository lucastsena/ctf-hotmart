import asyncio
import websockets
import hashlib
import base64
import codecs

def binary_to_text(binary_string):
    # Divide a string binária em blocos de 7 bits
    binary_values = [binary_string[i:i+7] for i in range(0, len(binary_string), 7)]
    ascii_characters = []

    for bv in binary_values:
        decimal_value = int(bv, 2)
        # Garante que o valor decimal seja convertível em um caractere ASCII legível
        if 32 <= decimal_value <= 126:
            ascii_characters.append(chr(decimal_value))
        else:
            ascii_characters.append('?')  # Caractere substituto para valores não convertíveis

    return ''.join(ascii_characters)

def hex_to_text(hex_string):
    bytes_object = bytes.fromhex(hex_string)
    return bytes_object.decode('ascii')

def single_byte_xor(encoded, key):
    decoded_bytes = base64.b64decode(encoded)
    key = int(key, 16)
    return ''.join(chr(byte ^ key) for byte in decoded_bytes)

async def solve_challenge():
    uri = "wss://ctf-challenges.devops.hotmart.com/echo"
    
    async with websockets.connect(uri) as websocket:
        await websocket.send("start cryptomix")
        print("Comando enviado: start cryptomix")
        
        method = None
        sentence = None
        key = None
        
        while True:
            response = await websocket.recv()
            print(f"Mensagem recebida: {response}")
            
            if "invalid command" in response.lower():
                print("Comando inválido. Verifique o comando enviado.")
                break

            if "Bem-Vindo ao HotCTF" in response:
                continue

            if "[=][=] CRYPTOMIX [=][=]" in response:
                print("Desafio iniciado. Aguardando primeira sentença.")
                continue
            
            if "Stage" in response:
                print("Novo estágio detectado.")
                method = None
                sentence = None
                key = None
                continue

            lines = response.splitlines()
            
            for line in lines:
                if "Method:" in line:
                    method = line.split("Method:")[1].strip().lower()
                elif "Encoded:" in line or "Sentence:" in line:
                    sentence = line.split("Encoded:")[1].strip() if "Encoded:" in line else line.split("Sentence:")[1].strip()
                elif "Key:" in line:
                    key = line.split("Key:")[1].strip()

            if method and sentence:
                if method == "md5":
                    result = hashlib.md5(sentence.encode()).hexdigest()
                elif method == "sha1":
                    result = hashlib.sha1(sentence.encode()).hexdigest()
                elif method == "sha256":
                    result = hashlib.sha256(sentence.encode()).hexdigest()
                elif method == "base64":
                    result = base64.b64decode(sentence).decode('utf-8')
                elif method == "binary":
                    result = binary_to_text(sentence)
                elif method == "rot-13":
                    result = codecs.decode(sentence, 'rot_13')
                elif method == "single_byte_xor":
                    if key:
                        result = single_byte_xor(sentence, key)
                    else:
                        print("Chave não encontrada para o método single_byte_xor")
                        continue
                elif method == "hex":
                    result = hex_to_text(sentence)
                else:
                    result = "_".join(list(sentence))
                
                print(f"Resultado gerado: {result}")
                
                await websocket.send(result)
                print("Resultado enviado ao servidor.")
                
                method = None
                sentence = None
                key = None

asyncio.run(solve_challenge())
