# Importa o módulo nmap para escaneamento de rede
import nmap

# Módulo para interação com banco de dados SQLite
import sqlite3

# Permite execução de comandos do sistema (usado para acessar ARP)
import subprocess

# Expressões regulares, útil para filtrar MAC address
import re

# Usado para operações de rede como hostname e IP
import socket

# Usado para obter informações sobre as interfaces de rede
import psutil

# Manipulação de data e hora
from datetime import datetime, timedelta

# Requisições HTTP (usado para buscar fabricante por API)
import requests

# Caminho do banco de dados SQLite
DB_PATH = "monitoramento.db"

# Dicionário com prefixos de MAC (OUI), fabricantes e tipo de dispositivo
FABRICANTES = {
    "00:1E:65": ("Dell", "PC"),
    "F0:79:59": ("Lenovo", "PC"),
    "E0:D5:5E": ("HP", "PC"),
    "3C:A8:2A": ("Acer", "PC"),
    "B4:2E:99": ("Asus", "PC"),
    "00:03:93": ("Toshiba", "PC"),
    "D4:6A:6A": ("Apple", "iPhone"),
    "68:5B:35": ("Apple", "Mac"),
    "A4:5E:60": ("Apple", "iPad"),
    "A4:77:33": ("Samsung", "Telefone"),
    "FC:FC:48": ("Huawei", "Telefone"),
    "3C:07:54": ("Xiaomi", "Telefone"),
    "54:99:63": ("Motorola", "Telefone"),
    "74:23:44": ("Realme", "Telefone"),
    "00:0E:8F": ("HTC", "Telefone"),
    "00:1A:11": ("HP", "Impressora"),
    "28:37:37": ("Canon", "Impressora"),
    "AC:84:C6": ("Epson", "Impressora"),
    "00:21:5C": ("Cisco", "Roteador"),
    "B8:27:EB": ("Raspberry Pi", "Dispositivo IoT"),
    "60:38:E0": ("TP-Link", "Roteador"),
    "F4:F2:6D": ("LG", "Smart TV")
}

# Consulta API pública para obter fabricante a partir do MAC
def buscar_fabricante_por_api(mac):
    try:
        url = f"https://api.macvendors.com/{mac}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            fabricante = response.text.strip()
            return fabricante
    except Exception as e:
        print(f"[Erro API fabricante]: {e}")
    return "Desconhecido"

# Identifica fabricante e tipo de dispositivo a partir do MAC address
def identificar_fabricante(mac):
    if not mac or mac == "Desconhecido":
        return ("Desconhecido", "Desconhecido")

    mac_formatado = mac.upper().replace("-", ":")
    prefixo = ":".join(mac_formatado.split(":")[:3])

    # Verifica se o prefixo está no dicionário local
    if prefixo in FABRICANTES:
        return FABRICANTES[prefixo]

    # Caso contrário, tenta buscar pela API
    fabricante = buscar_fabricante_por_api(mac_formatado)
    if fabricante != "Desconhecido":
        return (fabricante, "Desconhecido")

    return ("Desconhecido", "Desconhecido")

# Retorna o MAC address da interface de rede da própria máquina
def obter_mac_real_da_maquina():
    ip_local = obter_ip_local()
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address == ip_local:
                for addr in addrs:
                    if hasattr(psutil, 'AF_LINK') and addr.family == psutil.AF_LINK:
                        return addr.address.upper().replace("-", ":")
                    elif hasattr(socket, 'AF_PACKET') and addr.family == socket.AF_PACKET:
                        return addr.address.upper().replace("-", ":")
    return "Desconhecido"

# Obtém o MAC address de um IP da rede via tabela ARP
def obter_mac_via_arp(ip_alvo):
    try:
        output = subprocess.check_output("arp -a", shell=True).decode(errors="ignore")
        for linha in output.splitlines():
            if ip_alvo in linha:
                match = re.search(r"([0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2}", linha)
                if match:
                    mac = match.group(0).upper().replace("-", ":")
                    return mac
    except subprocess.SubprocessError as e:
        print(f"[ERRO] Falha ao executar comando ARP: {e}")
    except Exception as e:
        print(f"[ERRO] Erro inesperado ao obter MAC via ARP: {e}")
    return "Desconhecido"

# Retorna o IP local da máquina
def obter_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

# Tenta obter o nome da máquina (hostname) pelo IP
def obter_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return "Desconhecido"

# Retorna o range de IP da rede (ex: 192.168.1.0/24)
def obter_faixa_ip():
    try:
        ip_local = obter_ip_local()
        return "".join(ip_local.rsplit(".", 1)[0]) + ".0/24"
    except Exception:
        return "192.168.0.0/24"

# Realiza escaneamento da rede, salva no banco e retorna os dispositivos
def escanear_rede():
    rede = obter_faixa_ip()
    print(f"Escaneando rede: {rede}")

    scanner = nmap.PortScanner()
    scanner.scan(hosts=rede, arguments="-sn")

    dispositivos = []
    macs_detectados = set()
    ip_local = obter_ip_local()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for ip in scanner.all_hosts():
        hostname = obter_hostname(ip)

        if ip == ip_local:
            mac = obter_mac_real_da_maquina()
        else:
            mac = scanner[ip]['addresses'].get('mac', 'Desconhecido')
            if mac == 'Desconhecido':
                mac = obter_mac_via_arp(ip)

        macs_detectados.add(mac)

        fabricante, tipo = identificar_fabricante(mac)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("SELECT id FROM dispositivos WHERE mac = ?", (mac,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE dispositivos SET ip=?, hostname=?, fabricante=?, tipo=?, ultima_verificacao=?, online=1
                WHERE mac=?
            """, (ip, hostname, fabricante, tipo, timestamp, mac))
        else:
            cursor.execute("""
                INSERT INTO dispositivos (ip, mac, online, ultima_verificacao, fabricante, tipo, hostname)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ip, mac, 1, timestamp, fabricante, tipo, hostname))

        dispositivos.append({
            "ip": ip,
            "mac": mac,
            "hostname": hostname,
            "fabricante": fabricante,
            "tipo": tipo,
            "online": True
        })

    if macs_detectados:
        placeholders = ','.join('?' for _ in macs_detectados)
        cursor.execute(f"""
            UPDATE dispositivos
            SET online = 0
            WHERE mac NOT IN ({placeholders})
        """, tuple(macs_detectados))

    conn.commit()
    conn.close()
    return dispositivos

# Lista os dispositivos salvos no banco que estão na mesma subrede
def listar_dispositivos_mesma_rede():
    ip_local = obter_ip_local()
    if not ip_local:
        print("IP local não encontrado.")
        return []

    subrede = ".".join(ip_local.split('.')[:3])
    agora = datetime.now()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ip, mac, hostname, fabricante, tipo, ultima_verificacao, online
        FROM dispositivos
        WHERE ip LIKE ?
    """, (f"{subrede}.%",))

    dispositivos = []
    for row in cursor.fetchall():
        dispositivo_id = row[0]
        ultima_verificacao_str = row[6]
        online = bool(row[7])

        try:
            ultima_verificacao_dt = datetime.strptime(ultima_verificacao_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            ultima_verificacao_dt = agora - timedelta(minutes=5)

        if abs((agora - ultima_verificacao_dt).total_seconds()) > 300 and online:
            cursor.execute("UPDATE dispositivos SET online = 0 WHERE id = ?", (dispositivo_id,))
            online = False

        dispositivos.append({
            "ip": row[1],
            "mac": row[2],
            "hostname": row[3],
            "fabricante": row[4],
            "tipo": row[5],
            "ultima_verificacao": row[6],
            "online": online
        })

    conn.commit()
    conn.close()
    return dispositivos

# Remove do banco os dispositivos da mesma subrede
def deletar_dispositivos_mesma_rede():
    ip_local = obter_ip_local()
    if not ip_local:
        print("IP local não encontrado.")
        return False

    subrede = ".".join(ip_local.split('.')[:3])

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dispositivos WHERE ip LIKE ?", (f"{subrede}.%",))
            conn.commit()
            return True
    except Exception as e:
        print("Erro ao deletar dispositivos:", e)
        return False

# Executa escaneamento e listagem se rodar diretamente este script
if __name__ == "__main__":
    print("Iniciando varredura da rede...")
    dispositivos_encontrados = escanear_rede()
    print("\nDispositivos detectados:")
    for d in dispositivos_encontrados:
        print(d)

    print("\nDispositivos salvos na mesma rede:")
    mesmos_dispositivos = listar_dispositivos_mesma_rede()
    for d in mesmos_dispositivos:
        print(d)
