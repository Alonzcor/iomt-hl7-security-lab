import socket
import threading
from datetime import datetime

HOST = '127.0.0.1'
PORT = 2575

VT = b'\x0b'
FS_CR = b'\x1c\x0d'

def analizar_signos_vitales(mensaje_hl7):
    alertas = []
    for segmento in mensaje_hl7.split('\r'):
        if segmento.startswith("OBX|"):
            campos = segmento.split('|')
            if len(campos) >= 6:
                observacion = campos[3]
                try:
                    valor = float(campos[5])
                    if "8867-4" in observacion and (valor < 50 or valor > 120):
                        alertas.append(f"FRECUENCIA CARDÍACA CRÍTICA: {valor} bpm")
                    if "2708-6" in observacion and valor < 90:
                        alertas.append(f"HIPOXEMIA CRÍTICA (SpO2): {valor}%")
                except ValueError:
                    pass
    return alertas

def manejar_cliente(conn, addr):
    print(f"[NUEVA CONEXIÓN] Dispositivo conectado desde puerto efímero {addr[1]}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"[DESCONEXIÓN] Dispositivo en puerto {addr[1]} cerró sesión.\n")
                break
            
            mensaje_hl7 = data.strip(VT + FS_CR).decode('utf-8', errors='replace')
            hora = datetime.now().strftime("%H:%M:%S")
            alertas = analizar_signos_vitales(mensaje_hl7)
            
            print(f"--- Trama HL7 recibida [{hora}] desde puerto {addr[1]} ---")
            for segmento in mensaje_hl7.split('\r'):
                print(f"  {segmento}")
            
            if alertas:
                print("  >>> ¡¡¡ ALARMA CLÍNICA ACTIVADA EN CENTRAL !!! <<<")
                for alerta in alertas:
                    print(f"      [!] {alerta}")
            print("-" * 52)
            
            # La central confía ciegamente en cualquier conexión y responde ACK (AA)
            ack = VT + b"MSH|^~\\&|CENTRAL|HOSPITAL|MONITOR_UCI|CAMA_04|||ACK^R01|1|P|2.5\rMSA|AA|1" + FS_CR
            conn.sendall(ack)

def iniciar_central():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        
        print(f"[CENTRAL DE ENFERMERÍA] Escuchando en {HOST}:{PORT} (HL7 v2.5 / MLLP)")
        print("Modo multicliente activo. Esperando dispositivos médicos...\n")
        
        while True:
            conn, addr = server_socket.accept()
            hilo = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
            hilo.start()

if __name__ == "__main__":
    try:
        iniciar_central()
    except KeyboardInterrupt:
        print("\n[CENTRAL DE ENFERMERÍA] Servidor detenido.")
