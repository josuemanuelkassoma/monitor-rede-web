// src/pages/SessoesTrafego.jsx
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

function SessoesTrafego() {
  const [sessao, setSessao] = useState(null);
  const [duracao, setDuracao] = useState(0);
  const [maquina, setMaquina] = useState(null);
  const intervalRef = useRef(null);

  // Busca info da máquina
  useEffect(() => {
    axios.get('http://localhost:5000/maquina')
      .then(res => setMaquina(res.data))
      .catch(() => {});
  }, []);

  // Contador de duração
  useEffect(() => {
    if (sessao && !sessao.fim) {
      intervalRef.current = setInterval(() => setDuracao(d => d + 1), 1000);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [sessao]);

  const formatarDuracao = segs => {
    const h = Math.floor(segs/3600), m = Math.floor((segs%3600)/60), s = segs%60;
    return `${h}h ${m}m ${s}s`;
  };

  const diagnosticarSessao = () => {
    if (!sessao || sessao.total_usado_mb == null) return '';
    const total = sessao.total_usado_mb;
    if (total < 10) return 'Leve';
    if (total < 50) return 'Moderado';
    return 'Alto';
  };

  const iniciarSessao = async () => {
    const res = await axios.post('http://localhost:5000/trafego/sessao/iniciar');
    setSessao({ inicio: res.data.inicio });
    setDuracao(0);
  };

  const finalizarSessao = async () => {
    const res = await axios.post('http://localhost:5000/trafego/sessao/finalizar');
    setSessao(prev => ({
      ...prev,
      fim: res.data.fim,
      download_usado_mb: res.data.download_usado_mb,
      upload_usado_mb: res.data.upload_usado_mb,
      total_usado_mb: res.data.total_usado_mb
    }));
  };

  const iniciou = sessao && !sessao.fim;
  const finalizou = sessao && sessao.fim;

  return (
    <div style={{ padding: '2rem', position: 'relative' }}>
      {iniciou && (
        <div style={contadorStyle}>{formatarDuracao(duracao)}</div>
      )}
      <h1 style={titleStyle}>Sessões de Tráfego</h1>

      <div style={buttonRow}>
        <button
          onClick={iniciarSessao}
          disabled={iniciou}
          style={startBtn(iniciou)}
        >
          Iniciar Sessão
        </button>
        <button
          onClick={finalizarSessao}
          disabled={!iniciou}
          style={endBtn(!iniciou)}
        >
          Finalizar Sessão
        </button>
      </div>

      {sessao && (
        <>
          <table style={tableStyle}>
            <thead>
              <tr style={headerRow}>
                {['Início','Duração','Fim','Download','Upload','Total','Diagnóstico'].map(h => (
                  <th key={h} style={cellStyle}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={cellStyle}>{sessao.inicio}</td>
                <td style={cellStyle}>{formatarDuracao(duracao)}</td>
                <td style={cellStyle}>{sessao.fim ?? '-'}</td>
                <td style={cellStyle}>{sessao.download_usado_mb ?? '-'}</td>
                <td style={cellStyle}>{sessao.upload_usado_mb ?? '-'}</td>
                <td style={cellStyle}>{sessao.total_usado_mb ?? '-'}</td>
                <td style={cellStyle}>{finalizou ? diagnosticarSessao() : '-'}</td>
              </tr>
            </tbody>
          </table>
        </>
      )}
      
      {maquina && (
        <div style={footerStyle}>
          <div style={colStyle}>
            <p><strong>IP:</strong><br/>{maquina.ip}</p>
          </div>
          <div style={colStyle}>
            <p><strong>MAC:</strong><br/>{maquina.mac}</p>
          </div>
          <div style={colStyle}>
            <p><strong>Hostname:</strong><br/>{maquina.hostname}</p>
          </div>
        </div>
      )}
    </div>
  );
}

// Styles
const contadorStyle = {
  position: 'absolute', top: '1rem', right: '1rem',
  fontSize: '1.5rem', fontWeight: 'bold',
  backgroundColor: '#eef', padding: '0.5rem 1rem', borderRadius: '5px'
};
const titleStyle = { fontSize: '2rem', fontWeight: 'bold', marginBottom: '1.5rem' };
const buttonRow = { display: 'flex', gap: '1rem', marginBottom: '2rem' };
const startBtn = active => ({
  flex: 1, padding: '12px', backgroundColor: active ? '#aaa' : '#28a745',
  color: 'white', border: 'none', borderRadius: '5px', cursor: active ? 'not-allowed' : 'pointer'
});
const endBtn = active => ({
  flex: 1, padding: '12px', backgroundColor: active ? '#aaa' : '#dc3545',
  color: 'white', border: 'none', borderRadius: '5px', cursor: active ? 'not-allowed' : 'pointer'
});
const tableStyle = { width: '100%', borderCollapse: 'collapse', marginBottom: '1rem' };
const headerRow = { backgroundColor: '#f0f0f0' };
const cellStyle = { border: '1px solid #ccc', padding: '8px', textAlign: 'center' };
const footerStyle = {
  display: 'flex', gap: '2rem', backgroundColor: '#eef',
  padding: '1rem', borderRadius: '5px'
};
const colStyle = { flex: 1, textAlign: 'center' };

export default SessoesTrafego;
