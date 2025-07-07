// src/pages/Trafego.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Trafego() {
  const [trafego, setTrafego] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [maquina, setMaquina] = useState(null);
  const API_URL = "https://mynetwork-egj2.onrender.com";

  useEffect(() => {
    // obter info da máquina local
    axios.get(`${API_URL}/maquina`)
      .then(res => setMaquina(res.data))
      .catch(() => setMaquina(null));
  }, []);

  const iniciarMonitor = async () => {
    setCarregando(true);
    setTrafego(null);

    try {
      const res = await axios.get(`${API_URL}/trafego`);
      setTrafego(res.data.trafego);
    } catch {
      setTrafego({ erro: 'Erro ao medir tráfego.' });
    }

    setCarregando(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '2rem' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1.5rem' }}>
        Monitoramento de Tráfego
      </h1>

      <button
        onClick={iniciarMonitor}
        disabled={carregando}
        style={{
          width: '120px',
          height: '120px',
          borderRadius: '50%',
          backgroundColor: '#28a745',
          color: 'white',
          fontWeight: 'bold',
          fontSize: '1rem',
          border: 'none',
          marginBottom: '2rem',
          cursor: carregando ? 'not-allowed' : 'pointer',
        }}
      >
        {carregando ? 'Monitorando…' : 'Iniciar Monitor'}
      </button>

      {trafego && !trafego.erro && (
        <div style={{
          backgroundColor: '#f5f5f5',
          padding: '1.5rem',
          borderRadius: '10px',
          width: '100%',
          maxWidth: '500px',
          boxShadow: '0 0 10px rgba(0,0,0,0.1)'
        }}>
          <h3>Resultado</h3>
          <p><strong>Download:</strong> {trafego.download_mb} MB</p>
          <p><strong>Upload:</strong> {trafego.upload_mb} MB</p>
          <p><strong>Total:</strong> {trafego.total_mb} MB</p>
          <p><strong>Data:</strong> {trafego.data}</p>
          <hr style={{ margin: '1rem 0' }}/>
          <p style={{ fontSize: '0.9rem', color: '#555' }}>
            *Este valor é acumulado desde o boot do sistema.
          </p>
          
          {maquina && (
            <>
              <hr />
              <h4>Informações da Máquina</h4>
              <p><strong>IP:</strong> {maquina.ip}</p>
              <p><strong>MAC:</strong> {maquina.mac}</p>
              <p><strong>Hostname:</strong> {maquina.hostname}</p>
            </>
          )}
        </div>
      )}

      {trafego && trafego.erro && (
        <p style={{ color: 'red', marginTop: '1rem' }}>{trafego.erro}</p>
      )}
    </div>
  );
}

export default Trafego;
