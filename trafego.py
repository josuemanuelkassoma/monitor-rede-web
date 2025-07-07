import psutil
import sqlite3
import socket
from datetime import datetime
from flask import Blueprint, jsonify

DB_PATH = "monitoramento.db"

# Blueprint para o tráfego
trafego_bp = Blueprint("trafego", __name__)

def buscar_ip_local():
    """Obtém informações da máquina local, incluindo hostname e IP."""
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

def medir_trafego_local():
    """Mede o tráfego de rede da máquina local e registra os dados no banco de dados."""
    ip = buscar_ip_local()
    io = psutil.net_io_counters()
    download = round(io.bytes_recv / (1024 * 1024), 2)  # Convertido para MB
    upload = round(io.bytes_sent / (1024 * 1024), 2)
    total = round(download + upload, 2)
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar se o dispositivo já está cadastrado
    cursor.execute("SELECT id, ip FROM dispositivos WHERE ip = ?", (ip,))
    dispositivo = cursor.fetchone()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formato ISO 8601
    
    if dispositivo:
        dispositivo_id, dispositivo_ip = dispositivo
        # Atualizar IP e última verificação
        cursor.execute("""
            UPDATE dispositivos 
            SET ip = ?, ultima_verificacao = ?, online = 1
            WHERE id = ?
        """, (ip, timestamp, dispositivo_id))
    else:
        # Insere novo dispositivo
        cursor.execute("""
            INSERT INTO dispositivos (ip, ultima_verificacao, online) 
            VALUES (?, ?, 1)
        """, (ip, timestamp))
        dispositivo_id = cursor.lastrowid
        dispositivo_ip = ip
    
    # Inserir registro de tráfego
    cursor.execute("""
        INSERT INTO trafego (dispositivo_id, download_mb, upload_mb, timestamp)
        VALUES (?, ?, ?, ?)
    """, (dispositivo_id, download, upload, timestamp))
    
    conn.commit()
    conn.close()
    
    resultado = {
        "data": timestamp,
        "dispositivo_ip": dispositivo_ip,
        "download_mb": download,
        "upload_mb": upload,
        "total_mb": total
    }
    
    print(f"[INFO] {resultado['data']} - IP: {resultado['dispositivo_ip']} | "
          f"Download: {resultado['download_mb']} MB | Upload: {resultado['upload_mb']} MB | Total: {resultado['total_mb']} MB")
    return resultado

def listar_trafego_local():
    """Lista os registros de tráfego da máquina local a partir do banco de dados."""
    ip = buscar_ip_local()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Busca o ID do dispositivo local
    cursor.execute("SELECT id FROM dispositivos WHERE ip = ?", (ip,))
    resultado = cursor.fetchone()
    
    if not resultado:
        print(f"[AVISO] Nenhum dispositivo encontrado com IP {ip}")
        conn.close()
        return []

    dispositivo_id = resultado[0]

    # Busca todos os registros de tráfego
    cursor.execute("""
        SELECT download_mb, upload_mb, timestamp 
        FROM trafego 
        WHERE dispositivo_id = ?
        ORDER BY timestamp DESC
    """, (dispositivo_id,))
    
    trafegos = cursor.fetchall()
    conn.close()

    registros = [
        {"download_mb": dl, "upload_mb": ul, "timestamp": ts}
        for dl, ul, ts in trafegos
    ]
    
    print(f"[INFO] {len(registros)} registros de tráfego encontrados para IP {ip}")
    return registros

def deletar_historico_trafego_local():
    ip = buscar_ip_local()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM dispositivos WHERE ip = ?", (ip,))
            res = cursor.fetchone()
            if not res:
                return False
            dispositivo_id = res[0]
            cursor.execute("DELETE FROM trafego WHERE dispositivo_id = ?", (dispositivo_id,))
            conn.commit()
            return True
    except Exception as e:
        print("Erro ao deletar tráfego:", e)
        return False



# Se executado diretamente, realiza um teste simples
if __name__ == "__main__":
    print("Iniciando monitoramento de tráfego de rede...")
    medir_trafego_local()
    # Opcional: testar também a listagem
    registros = listar_trafego_local()
    for r in registros:
        print(r)
