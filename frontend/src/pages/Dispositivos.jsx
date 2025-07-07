import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Dispositivos() {
  const [dispositivos, setDispositivos] = useState([]);
  const [maquina, setMaquina] = useState(null);
  const [loading, setLoading] = useState(false);
  const dataAtual = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const API_URL = "https://mynetwork-egj2.onrender.com";

  const carregarDispositivos = async () => {
    setLoading(true);
    setDispositivos([]); // Limpa a tabela enquanto busca os novos dados

    try {
      const res = await axios.get(`${API_URL}/devices`);
      setDispositivos(res.data.dispositivos || []);
    } catch (error) {
      console.error('Erro ao buscar dispositivos:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    axios.get(`${API_URL}/maquina`)
      .then(res => setMaquina(res.data))
      .catch(err => console.error("Erro ao buscar info da máquina:", err));
    carregarDispositivos();
  }, []);

  const isMaquinaLocal = (dispositivo) => {
    return (
      dispositivo.ip === maquina.ip &&
      dispositivo.mac === maquina.mac &&
      dispositivo.hostname === maquina.hostname
    );
  };

 const agora = new Date();

  const formatado = agora.toLocaleString('pt-BR', {
  day: '2-digit',
  month: '2-digit',
  year: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  second: '2-digit',
  hour12: false
});

  return (
    <div style={{ padding: '30px' }}>
      <section>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '1rem' }}>
          Dispositivos Conectados na Mesma Rede
        </h2>
        <h5>Obs: A máquina local é a destacada na tabela!</h5>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#e6f4ea' }}>
              <th style={cellStyle}>IP</th>
              <th style={cellStyle}>MAC</th>
              <th style={cellStyle}>Hostname</th>
              <th style={cellStyle}>Fabricante</th>
              <th style={cellStyle}>Tipo</th>
              <th style={cellStyle}>Última Verificação</th>
              <th style={cellStyle}>Online</th>
            </tr>
          </thead>
          <tbody>
            {dispositivos.length > 0 ? (
              dispositivos.map((d, i) => (
                <tr
                  key={i}
                  style={{
                    backgroundColor: isMaquinaLocal(d)
                    ? '#80dfff' // azul claro para máquina local
                    : d.ultima_verificacao?.startsWith(dataAtual)
                  }}
                >
                  <td style={cellStyle}>{d.ip || 'Desconhecido'}</td>
                  <td style={cellStyle}>{d.mac || 'Desconhecido'}</td>
                  <td style={cellStyle}>{d.hostname || 'Desconhecido'}</td>
                  <td style={cellStyle}>{d.fabricante || 'Desconhecido'}</td>
                  <td style={cellStyle}>{d.tipo || 'Desconhecido'}</td>
                  <td style={cellStyle}>{d.ultima_verificacao || formatado }</td>
                  <td style={cellStyle}>{d.online ? 'Sim' : 'Não'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" style={{ ...cellStyle, textAlign: 'center', color: '#888' }}>
                  {loading ? 'Carregando dispositivos...' : 'Nenhum dispositivo encontrado.'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      <div style={{ marginTop: '20px', textAlign: 'right' }}>
        <button
          onClick={carregarDispositivos}
          disabled={loading}
          style={{
            ...btnStyle,
            backgroundColor: loading ? '#ccc' : '#007bff',
            color: loading ? '#666' : '#fff',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          {loading ? 'Scaneando...!!' : '🔄 Refrescar'}
        </button>
      </div>
    </div>
  );
}

// Estilos
const cellStyle = {
  border: '1px solid #ccc',
  padding: '8px',
  textAlign: 'left'
};

const btnStyle = {
  padding: '10px 16px',
  fontSize: '1rem',
  border: 'none',
  borderRadius: '6px',
  transition: 'background-color 0.3s ease'
};

export default Dispositivos;
