// src/pages/Speedtest.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Speedtest() {
  const [velocidade, setVelocidade] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [maquina, setMaquina] = useState(null);
  const API_URL = "https://mynetwork-egj2.onrender.com";

  useEffect(() => {
   axios.get(`${API_URL}/maquina`)
      .then(res => setMaquina(res.data))
      .catch(() => setMaquina(null));
  }, []);

  const iniciarTeste = async () => {
    setCarregando(true);
    setVelocidade(null);

    try {
      const res = await axios.get(`${API_URL}/speedtest_module`);
      setVelocidade(res.data.velocidade);
    } catch {
      setVelocidade({ erro: 'Erro ao executar teste de velocidade.' });
    }

    setCarregando(false);
  };

  const interpretarRede = (download, upload, ping) => {
    if (download < 1 || upload < 0.5 || ping > 150) return 'Conexão instável. Ruim para jogos online ou vídeo chamadas.';
    if (download < 5 || upload < 1) return 'Conexão regular. Evite muitos dispositivos ao mesmo tempo.';
    if (download < 15) return 'Boa para vídeos em HD e navegação confortável.';
    return 'Excelente! Ideal para streaming, reuniões online e downloads pesados.';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '2rem' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>
        Teste de Velocidade
      </h1>

      <button
        onClick={iniciarTeste}
        disabled={carregando}
        style={{
          width: '120px',
          height: '120px',
          borderRadius: '50%',
          backgroundColor: '#007bff',
          color: 'white',
          fontWeight: 'bold',
          fontSize: '1rem',
          border: 'none',
          marginBottom: '2rem',
          cursor: carregando ? 'not-allowed' : 'pointer',
        }}
      >
        {carregando ? 'Testando...' : 'Iniciar Teste'}
      </button>

      {velocidade && !velocidade.erro && (
        <div style={{
          backgroundColor: '#f5f5f5',
          padding: '1.5rem',
          borderRadius: '10px',
          width: '100%',
          maxWidth: '600px',
          boxShadow: '0 0 10px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ marginBottom: '1rem' }}>Resultados</h3>
          <p><strong>Ping:</strong> {velocidade.ping_ms} ms</p>
          <p><strong>Download:</strong> {velocidade.download_mb} Mbps</p>
          <p><strong>Upload:</strong> {velocidade.upload_mb} Mbps</p>
          <p><strong>Data:</strong> {velocidade.timestamp}</p>
          <hr />
          <p><strong>Diagnóstico:</strong> {interpretarRede(velocidade.download_mb, velocidade.upload_mb, velocidade.ping_ms)}</p>

          {maquina && (
            <>
              <hr />
              <h4 style={{ marginTop: '1rem' }}>Informações da Máquina</h4>
              <p><strong>IP:</strong> {maquina.ip}</p>
              <p><strong>MAC:</strong> {maquina.mac}</p>
              <p><strong>Hostname:</strong> {maquina.hostname}</p>
            </>
          )}

          <hr />
          <h4 style={{ marginTop: '1rem' }}>Detalhes Técnicos</h4>
          <p>🛰️ <i>Servidor de teste escolhido automaticamente.</i> (Este campo pode ser personalizado se o backend retornar mais detalhes no futuro)</p>
        </div>
      )}

      {velocidade && velocidade.erro && (
        <p style={{ color: 'red', marginTop: '1rem' }}>{velocidade.erro}</p>
      )}
    </div>
  );
}

export default Speedtest;
