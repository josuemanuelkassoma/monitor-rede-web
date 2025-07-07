# ==== IMPORTAÇÕES ====

# Importa o módulo de conexão SQLite
import sqlite3

# Importa o Flask para criar a API, jsonify para respostas JSON
from flask import Flask, jsonify

# Importa o CORS para permitir requisições externas (como do frontend React)
from flask_cors import CORS

# ==== IMPORTAÇÕES DOS MÓDULOS PERSONALIZADOS ====

# Importa funções relacionadas ao monitoramento de dispositivos
from monitor import (
    escanear_rede,
    listar_dispositivos_mesma_rede,
    obter_ip_local,
    obter_hostname,
    obter_mac_real_da_maquina,
)

# Importa funções e Blueprint do módulo de tráfego
from trafego import medir_trafego_local, listar_trafego_local, trafego_bp

# Importa funções do módulo de speedtest
from speedtest_module import (
    medir_velocidade,
    listar_velocidades_da_maquina_local,
)

# Importa o Blueprint de sessões de tráfego
from sessoes import sessoes_bp

# ==== INICIALIZAÇÃO DA APLICAÇÃO ====

# Cria a aplicação Flask
app = Flask(__name__)

# Ativa CORS para permitir acesso de qualquer origem (útil para frontend separado)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ==== FUNÇÕES AUXILIARES ====

def get_db_connection():
    """
    Cria e retorna uma conexão com o banco de dados SQLite,
    configurando para que cada linha seja retornada como um dicionário.
    """
    conn = sqlite3.connect("monitoramento.db")
    conn.row_factory = sqlite3.Row
    return conn

# ==== ROTAS BÁSICAS ====

@app.route("/")
def home():
    """Rota principal para verificar se a API está no ar."""
    return jsonify({"message": "API de Monitoramento de Rede Local"})

@app.route("/ping")
def ping():
    """Rota de verificação de status da API."""
    return jsonify({"status": "ok", "message": "API funcionando"})

# ==== ROTAS DA MÁQUINA LOCAL ====

@app.route("/maquina")
def maquina_local():
    """
    Retorna informações da máquina local (IP, MAC e hostname).
    """
    ip = obter_ip_local()
    mac = obter_mac_real_da_maquina()
    hostname = obter_hostname(ip)
    return jsonify({
        "ip": ip,
        "mac": mac,
        "hostname": hostname
    })

# ==== ROTAS DE DISPOSITIVOS ====

@app.route("/dispositivos/rede")
def dispositivos_mesma_rede():
    """Lista dispositivos salvos que estão na mesma sub-rede da máquina local."""
    dispositivos = listar_dispositivos_mesma_rede()
    return jsonify({"dispositivos": dispositivos})

@app.route("/devices")
def listar_dispositivos():
    """Escaneia a rede atual e retorna os dispositivos ativos encontrados."""
    try:
        dispositivos = escanear_rede()
        return jsonify({"dispositivos": dispositivos})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/devices/db")
def listar_dispositivos_salvos():
    """
    Lista todos os dispositivos armazenados no banco de dados,
    ordenados pela última verificação.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dispositivos ORDER BY ultima_verificacao DESC")
        rows = cursor.fetchall()
        conn.close()

        dispositivos = []
        for row in rows:
            dispositivos.append({
                "id": row["id"],
                "ip": row["ip"],
                "mac": row["mac"],
                "fabricante": row["fabricante"],
                "tipo": row["tipo"],
                "online": bool(row["online"]),
                "hostname": row["hostname"],
                "ultima_verificacao": row["ultima_verificacao"]
            })
        return jsonify({"dispositivos": dispositivos})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ==== ROTAS DE SPEEDTEST ====

@app.route("/speedtest_module")
def executar_speedtest():
    """Executa um teste de velocidade e retorna os resultados (ping, download, upload)."""
    try:
        resultado = medir_velocidade()
        return jsonify({"velocidade": resultado})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/speedtest/historico")
def speedtest_historico():
    """Retorna o histórico de testes de velocidade da máquina local."""
    try:
        historico = listar_velocidades_da_maquina_local()
        return jsonify({"historico": historico})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ==== ROTAS DE TRÁFEGO ====

@app.route("/trafego")
def exibir_trafego():
    """Mede e retorna o tráfego atual de rede da máquina (download/upload)."""
    try:
        trafego = medir_trafego_local()
        return jsonify({"trafego": trafego})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/trafego/historico")
def trafego_historico():
    """Retorna o histórico completo de medições de tráfego da máquina local."""
    try:
        historico = listar_trafego_local()
        return jsonify({"historico": historico})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ==== ROTAS DE EXCLUSÃO ====

@app.route("/deletar/dispositivos", methods=["DELETE"])
def deletar_dispositivos():
    """Deleta os dispositivos da mesma sub-rede armazenados no banco."""
    from monitor import deletar_dispositivos_mesma_rede
    if deletar_dispositivos_mesma_rede():
        return jsonify({"mensagem": "Dispositivos deletados com sucesso"})
    return jsonify({"erro": "Erro ao deletar"}), 500

@app.route("/deletar/sessoes", methods=["DELETE"])
def deletar_sessoes():
    """Deleta o histórico de sessões de tráfego da máquina local."""
    from sessoes import deletar_sessoes_da_maquina_local
    if deletar_sessoes_da_maquina_local():
        return jsonify({"mensagem": "Sessões deletadas com sucesso"})
    return jsonify({"erro": "Erro ao deletar"}), 500

@app.route("/deletar/speedtest", methods=["DELETE"])
def deletar_speedtest():
    """Deleta o histórico de testes de velocidade da máquina local."""
    from speedtest_module import deletar_historico_speedtest_local
    if deletar_historico_speedtest_local():
        return jsonify({"mensagem": "Histórico de speedtest deletado com sucesso"})
    return jsonify({"erro": "Erro ao deletar"}), 500

@app.route("/deletar/trafego", methods=["DELETE"])
def deletar_trafego():
    """Deleta o histórico de tráfego da máquina local."""
    from trafego import deletar_historico_trafego_local
    if deletar_historico_trafego_local():
        return jsonify({"mensagem": "Histórico de tráfego deletado com sucesso"})
    return jsonify({"erro": "Erro ao deletar"}), 500

# ==== REGISTRO DOS BLUEPRINTS ====

# Registra o Blueprint de sessões de tráfego (rotas agrupadas)
app.register_blueprint(sessoes_bp)

# Registra o Blueprint de tráfego (rotas agrupadas)
app.register_blueprint(trafego_bp)

# ==== EXECUÇÃO DA APLICAÇÃO ====

# Executa a aplicação Flask em modo debug
if __name__ == "__main__":
    app.run(debug=True)
