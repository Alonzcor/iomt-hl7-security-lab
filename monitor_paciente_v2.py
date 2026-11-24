import socket
import time
import random
from datetime import datetime

HOST = '127.0.0.1'
PORT = 2575

VT = b'\x0b'
FS_CR = b'\x1c\x0d'

def generar_trama_hl7(msg_id, hr, spo2):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Datos 100% ficticios para demostración segura
    segmentos = [
        f"MSH|^~\\&|MONITOR_UCI|CAMA_04|CENTRAL|HOSPITAL|{timestamp}||ORU^R01|{msg_id}|P|2.5",
        "PID|1||ID0001^^^HOSPITAL^MR||PACIENTE^PRUEBA^CAMA04||19900101|M",
        f"OBX|1|NM|8867-4^Frecuencia Cardiaca^LN||{hr}|bpm|60-100|N|||F",
        f"OBX|2|NM|2708-6^Saturacion Oxigeno^LN||{spo2}|%|95-100|N|||F"
    ]
    cuerpo = "\r".join(segmentos).encode('utf-8')
    return VT + cuerpo + FS_CR

def iniciar_monitor():
    print(f"[MONITOR UCI - CAMA 04] Conectando a Central en {HOST}:{PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        print("[CONECTADO] Transmitiendo signos vitales normales cada 2 segundos...\n")
        
        msg_id = 1
        while True:
            hr = random.randint(68, 84)
            spo2 = random.randint(96, 99)
            
            trama = generar_trama_hl7(msg_id, hr, spo2)
            client_socket.sendall(trama)
            print(f"[MONITOR LEGÍTIMO #{msg_id}] FC: {hr} bpm | SpO2: {spo2}%")
            
            client_socket.recv(1024)
            msg_id += 1
            time.sleep(2)

if __name__ == "__main__":
    try:
        iniciar_monitor()
    except ConnectionRefusedError:
        print("[ERROR] Ejecuta primero 'central_enfermeria_v2.py'.")
    except KeyboardInterrupt:
        print("\n[MONITOR UCI] Detenido.")
