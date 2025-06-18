# speedtest_module.py
import speedtest 
import sqlite3
import socket
from datetime import datetime
from flask import Blueprint, jsonify
from monitor import obter_mac_real_da_maquina


# Blueprint para agrupar rotas de speedtest
speed_bp = Blueprint('speed', __name__)

# Caminho para o banco de dados SQLite onde os dados serão armazenados
DB_PATH = "monitoramento.db"

def buscar_ip_local():
    """Obtém informações da máquina local, incluindo hostname e IP."""
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

def obter_ip_maquina_local():
    """
    Obtém informações da máquina local, incluindo:
    - Endereço IP local
    - Hostname
    """
    try:
        hostname = socket.gethostname()  # Nome do host da máquina
        ip_local = socket.gethostbyname(hostname)  # Endereço IP associado
        return ip_local, hostname
    except Exception as e:
        print("Erro ao obter dados da máquina local:", e)
    return None, None

def registrar_ou_atualizar_dispositivo():
    """
    Registra ou atualiza as informações do dispositivo no banco de dados.
    Se o dispositivo já existir no banco, apenas atualiza o registro.
    Retorna o ID do dispositivo.
    """
    ip, hostname = obter_ip_maquina_local()
    mac = obter_mac_real_da_maquina()
    if not ip:
        return None  # Se não conseguiu obter o IP, não prossegue
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Verifica se o dispositivo já existe
        cursor.execute("SELECT id, ip, hostname FROM dispositivos WHERE ip = ?", (ip,))
        dispositivo = cursor.fetchone()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formato ISO

        if dispositivo:
            dispositivo_id, ip_antigo, hostname_antigo = dispositivo
            # Atualiza se IP ou hostname mudaram
            if ip_antigo != ip or hostname_antigo != hostname:
                cursor.execute("""
                    UPDATE dispositivos
                    SET ip = ?, hostname = ?, mac = ?, ultima_verificacao = ?, online = 1
                    WHERE id = ?
                """, (ip, hostname, mac, timestamp, dispositivo_id))
                conn.commit()
            return dispositivo_id
        else:
            # Insere novo registro
            cursor.execute("""
                INSERT INTO dispositivos (ip, hostname, mac, ultima_verificacao, online)
                VALUES (?, ?, ?, ?, 1)
            """, (ip, hostname, mac, timestamp))
            conn.commit()
            return cursor.lastrowid

def medir_velocidade():
    """
    Mede a velocidade da conexão de internet com speedtest.
    Retorna: ping (ms), download (Mbps), upload (Mbps) e timestamp.
    Armazena o resultado no BD.
    """
    try:
        st = speedtest.Speedtest()
        st.get_best_server()  # Seleciona melhor servidor
        
        # Converte de bits → megabits
        download = round(st.download() / (1024 * 1024), 2)
        upload = round(st.upload() / (1024 * 1024), 2)
        ping = round(st.results.ping, 2)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        dispositivo_id = registrar_ou_atualizar_dispositivo()
        if not dispositivo_id:
            return {"erro": "Falha ao registrar ou atualizar dispositivo"}

        # Insere dados de velocidade
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO velocidade (dispositivo_id, ping_ms, download_mb, upload_mb, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (dispositivo_id, ping, download, upload, timestamp))
            conn.commit()

        resultado = {
            "dispositivo_id": dispositivo_id,
            "ping_ms": ping,
            "download_mb": download,
            "upload_mb": upload,
            "timestamp": timestamp
        }
        return resultado

    except Exception as e:
        import traceback
        print("Erro ao medir velocidade da internet:")
        traceback.print_exc()
        return {"erro": f"Falha na medição de velocidade: {str("Sem Rede Conectada!, precisa se conectar a uma rede!")}"}

def listar_velocidades_da_maquina_local():
    """
    Lista todos os registros de velocidade da máquina local (pelo IP).
    Retorna lista de { ping_ms, download_mb, upload_mb, timestamp }.
    """
    ip_local, _ = obter_ip_maquina_local()
    if not ip_local:
        print("IP local não encontrado.")
        return []

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Busca ID do dispositivo local
        cursor.execute("SELECT id FROM dispositivos WHERE ip = ?", (ip_local,))
        resultado = cursor.fetchone()
        if not resultado:
            print("Dispositivo local não encontrado no banco de dados.")
            return []
        dispositivo_id = resultado[0]

        # Seleciona históricos de velocidade
        cursor.execute("""
            SELECT ping_ms, download_mb, upload_mb, timestamp
            FROM velocidade
            WHERE dispositivo_id = ?
            ORDER BY timestamp DESC
        """, (dispositivo_id,))

        registros = []
        for row in cursor.fetchall():
            registros.append({
                "ping_ms": row[0],
                "download_mb": row[1],
                "upload_mb": row[2],
                "timestamp": row[3]
            })
        return registros
    
def deletar_historico_speedtest_local():
    ip =  buscar_ip_local()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM dispositivos WHERE ip = ?", (ip,))
            res = cursor.fetchone()
            if not res:
                return False
            dispositivo_id = res[0]
            cursor.execute("DELETE FROM velocidade WHERE dispositivo_id = ?", (dispositivo_id,))
            conn.commit()
            return True
    except Exception as e:
        print("Erro ao deletar speedtest:", e)
        return False


# Se executar diretamente, apenas demonstra no console
if __name__ == "__main__":
    print("Medindo a velocidade da rede...")
    print(medir_velocidade())
    print("\nHistórico de velocidade da máquina local:")
    for registro in listar_velocidades_da_maquina_local():
        print(registro)
