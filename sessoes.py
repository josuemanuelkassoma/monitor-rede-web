import sqlite3
import psutil
import socket
from datetime import datetime
from flask import Blueprint, jsonify, request

DB_PATH = "monitoramento.db"

# Definição do Blueprint para gerenciamento das sessões
sessoes_bp = Blueprint("sessoes", __name__)

# Função para obter o tráfego de rede atual em MB
def get_rede_atual_mb():
    io = psutil.net_io_counters()
    return round(io.bytes_recv / (1024 * 1024), 2), round(io.bytes_sent / (1024 * 1024), 2)


# Obtém dados da máquina local (IP e MAC)
def obter_ip_maquina_local():
    try:
        ip_local = socket.gethostbyname(socket.gethostname())

        return {"ip": ip_local}
    except Exception as e:
        print("Erro ao obter ip da máquina local:", e)
        return None

# Registra o dispositivo local no banco de dados
def registrar_dispositivo_local():
    dados = obter_ip_maquina_local()
    if not dados:
        return None  # Se não foi possível obter os dados, retorna None
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM dispositivos WHERE ip = ?", (dados["ip"],))
        resultado = cursor.fetchone()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Formato ISO 8601

        if resultado:
            # Se o dispositivo já está registrado, apenas atualiza o IP e última verificação
            cursor.execute("""
                UPDATE dispositivos SET ip=?, ultima_verificacao=?
                WHERE ip=?
            """, (dados["ip"], timestamp, dados["ip"]))
            dispositivo_id = resultado[0]
        else:
            # Caso contrário, insere um novo registro para o dispositivo
            cursor.execute("""
                INSERT INTO dispositivos (ip, online, ultima_verificacao)
                VALUES (?, ?, ?)
            """, (dados["ip"], 1, timestamp))
            dispositivo_id = cursor.lastrowid
        conn.commit()
    
    return dispositivo_id

# Obtém o ID do dispositivo atual
def obter_dispositivo_id():
    return registrar_dispositivo_local()

# Rota para iniciar uma sessão de monitoramento de tráfego
@sessoes_bp.route("/trafego/sessao/iniciar", methods=["POST"])
def iniciar_sessao():
    dispositivo_id = obter_dispositivo_id()
    if not dispositivo_id:
        return jsonify({"erro": "Falha ao registrar ou obter dispositivo"}), 400
    print({"erro": "Falha ao registrar ou obter dispositivo"})

    download, upload = get_rede_atual_mb()
    inicio = datetime.now()

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Verifica se já existe uma sessão ativa para o dispositivo
            cursor.execute("SELECT id FROM sessoes WHERE dispositivo_id = ? AND fim IS NULL", (dispositivo_id,))
            if cursor.fetchone():
                return jsonify({"erro": "Já existe uma sessão ativa para este dispositivo"}), 400
            
            # Insere uma nova sessão no banco de dados
            cursor.execute("""
                INSERT INTO sessoes (dispositivo_id, inicio, download_inicial, upload_inicial, download_final, upload_final)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (dispositivo_id, inicio, download, upload, "null", "null"))
            conn.commit()
        
        return jsonify({
            "status": "Sessão iniciada",
            "dispositivo_id": dispositivo_id,
            "inicio": str(inicio),
            "download_inicial": download,
            "upload_inicial": upload
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Rota para finalizar uma sessão de monitoramento de tráfego
@sessoes_bp.route("/trafego/sessao/finalizar", methods=["POST"])
def finalizar_sessao():
    dispositivo_id = obter_dispositivo_id()
    if not dispositivo_id:
        return jsonify({"erro": "Dispositivo não registrado no banco de dados"}), 400
    
    download_final, upload_final = get_rede_atual_mb()
    fim = datetime.now()

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Obtém a sessão ativa para o dispositivo
            cursor.execute("""
                SELECT id, download_inicial, upload_inicial, inicio 
                FROM sessoes 
                WHERE dispositivo_id = ? AND fim IS NULL 
                ORDER BY id DESC LIMIT 1
            """, (dispositivo_id,))
            sessao = cursor.fetchone()

            if not sessao:
                return jsonify({"erro": "Nenhuma sessão iniciada encontrada para este dispositivo"}), 400

            sessao_id, d_ini, u_ini, inicio = sessao
            total_download = round(download_final - d_ini, 2)
            total_upload = round(upload_final - u_ini, 2)

            # Finaliza a sessão atualizando os valores finais no banco de dados
            cursor.execute("""
                UPDATE sessoes
                SET fim = ?, download_final = ?, upload_final = ?
                WHERE id = ?
            """, (fim, download_final, upload_final, sessao_id))
            conn.commit()
        
        return jsonify({
            "status": "Sessão finalizada",
            "dispositivo_id": dispositivo_id,
            "inicio": inicio,
            "fim": str(fim),
            "download_usado_mb": total_download,
            "upload_usado_mb": total_upload,
            "total_usado_mb": round(total_download + total_upload, 2)
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Rota para listar todas as sessões encerradas
@sessoes_bp.route("/trafego/sessoes", methods=["GET"])
def listar_sessoes():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, dispositivo_id, inicio, fim,
                       ROUND(download_final - download_inicial, 2) as download_usado,
                       ROUND(upload_final - upload_inicial, 2) as upload_usado
                FROM sessoes
                WHERE fim IS NOT NULL
                ORDER BY id DESC
            """)
            sessoes = [{
                "id": row[0],
                "dispositivo_id": row[1],
                "inicio": row[2],
                "fim": row[3],
                "download_usado_mb": row[4],
                "upload_usado_mb": row[5],
                "total_usado_mb": round(row[4] + row[5], 2)
            } for row in cursor.fetchall()]

        # Iterar sobre a lista de sessões e imprimir corretamente
        for sessao in sessoes:
            print(f"[INFO] ID: {sessao['dispositivo_id']} - INICIO: {sessao['inicio']} | FIM: {sessao['fim']} | DOWNLOAD_USADO: {sessao['download_usado_mb']} | UPLOAD_USADO: {sessao['upload_usado_mb']} | TOTAL_USADO: {sessao['total_usado_mb']} ")

        return jsonify({"sessoes": sessoes})
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
    # Rota para listar sessões por dispositivo (com base no IP da máquina local)
@sessoes_bp.route("/trafego/sessoes/dispositivo", methods=["GET"])
def listar_sessoes_por_dispositivo():
    """
    Lista todas as sessões encerradas associadas à máquina local.
    """
    dados = obter_ip_maquina_local()
    if not dados:
        return jsonify({"erro": "IP local não encontrado."}), 400

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Buscar ID do dispositivo com base no IP
            cursor.execute("SELECT id FROM dispositivos WHERE ip = ?", (dados["ip"],))
            resultado = cursor.fetchone()

            if not resultado:
                return jsonify({"erro": "Dispositivo não encontrado no banco de dados."}), 404

            dispositivo_id = resultado[0]

            # Buscar sessões finalizadas para esse dispositivo
            cursor.execute("""
                SELECT inicio, fim,
                       ROUND(download_final - download_inicial, 2),
                       ROUND(upload_final - upload_inicial, 2)
                FROM sessoes
                WHERE dispositivo_id = ? AND fim IS NOT NULL
                ORDER BY inicio DESC
            """, (dispositivo_id,))

            registros = []
            for row in cursor.fetchall():
                total = row[2] + row[3]
                registros.append({
                    "inicio": row[0],
                    "fim": row[1],
                    "download_usado_mb": row[2],
                    "upload_usado_mb": row[3],
                    "total_usado_mb": round(total, 2)
                })

        return jsonify({"sessoes": registros})
    
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def deletar_sessoes_da_maquina_local():
    dispositivo_id = obter_dispositivo_id()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessoes WHERE dispositivo_id = ?", (dispositivo_id,))
            conn.commit()
            return True
    except Exception as e:
        print("Erro ao deletar sessões:", e)
        return False



if __name__ == "__main__":
    print("Listando todas as sessoes...")
