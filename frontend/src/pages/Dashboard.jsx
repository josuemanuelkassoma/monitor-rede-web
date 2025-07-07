// src/pages/Dashboard.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const navigate = useNavigate();
  const [maquina, setMaquina] = useState(null);
  const [dispositivos, setDispositivos] = useState([]);
  const [botaoAtivo, setBotaoAtivo] = useState(null);
  const API_URL = "https://mynetwork-egj2.onrender.com";


  useEffect(() => {
    // Busca info da máquina local
       axios.get(`${API_URL}/maquina`)
      .then(res => setMaquina(res.data))
      .catch(err => console.error("Erro ao buscar info da máquina:", err));

    // Busca dispositivos na mesma rede
    axios.get(`${API_URL}/dispositivos/rede`)
      .then(res => {
        // Se a resposta vier dentro de um campo 'dispositivos', use-o
        const lista = Array.isArray(res.data)
          ? res.data
          : res.data.dispositivos || [];
        setDispositivos(lista);
      })
      .catch(err => console.error("Erro ao buscar dispositivos:", err));
  }, []);

  const handleNavigation = (path) => {
    setBotaoAtivo(path);
    navigate(path);
  };

  return (
    <div style={{ padding: '1rem' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1rem' }}>
        Dashboard
      </h1>

      {/* Boas-vindas */}
      <div style={{
        backgroundColor: '#f0f9ff',
        border: '1px solid #b6e0fe',
        borderRadius: '8px',
        padding: '1rem 1.5rem',
        marginBottom: '2rem',
        fontSize: '1.1rem',
        lineHeight: '1.6',
        color: '#0c4a6e'
      }}>
        <p style={{ margin: 0 }}>
          👋 Seja bem-vindo ao <strong>seu monitor de rede</strong>. Aqui você pode acompanhar o tráfego da sua rede, a velocidade, os dispositivos conectados e o histórico completo de monitoramentos realizados.
        </p>
      </div>

      {/* Máquina local */}
      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.8rem' }}>
          Informações da Máquina Local
        </h2>
        {maquina ? (
          <table style={{ width: '100%', maxWidth: '500px', borderCollapse: 'collapse', backgroundColor: '#f9fafb' }}>
            <tbody>
              <tr>
                <td style={infoCellLabel}>IP:</td>
                <td style={infoCellValue}>{maquina.ip}</td>
              </tr>
              <tr>
                <td style={infoCellLabel}>MAC:</td>
                <td style={infoCellValue}>{maquina.mac}</td>
              </tr>
              <tr>
                <td style={infoCellLabel}>Hostname:</td>
                <td style={infoCellValue}>{maquina.hostname}</td>
              </tr>
            </tbody>
          </table>
        ) : <p>Carregando informações...</p>}
      </section>

      {/* Ações */}
      <section style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          O que deseja monitorar?
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {[
            { path: '/trafego', label: 'Tráfego Total' },
            { path: '/sessoes-trafego', label: 'Tráfego Parcial' },
            { path: '/speedtest', label: 'Velocidade da Rede' },
            { path: '/dispositivos', label: 'Dispositivos Conectados à Rede' },
            { path: '/historico', label: 'Histórico da Rede' },
          ].map(({ path, label }) => (
            <button
              key={path}
              onClick={() => handleNavigation(path)}
              style={{
                ...btnStyle,
                backgroundColor: botaoAtivo === path ? '#cce7ff' : '#e0e0e0',
              }}
              onMouseEnter={e => e.currentTarget.style.backgroundColor = '#d7eaff'}
              onMouseLeave={e => e.currentTarget.style.backgroundColor = botaoAtivo === path ? '#cce7ff' : '#e0e0e0'}
            >
              {label}
            </button>
          ))}
        </div>
      </section>

      {/* Tabela de dispositivos */}
      <section>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          Dispositivos Registrados na Mesma Rede
        </h2>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f0f0f0' }}>
              <th style={cellStyle}>IP</th>
              <th style={cellStyle}>MAC</th>
              <th style={cellStyle}>Hostname</th>
              <th style={cellStyle}>Data</th>
            </tr>
          </thead>
          <tbody>
            {dispositivos.map((d, i) => (
              <tr
                key={i}
                style={{ backgroundColor: d.online ? '#d1fae5' : '#fecaca' }}
              >
                <td style={cellStyle}>{d.ip}</td>
                <td style={cellStyle}>{d.mac}</td>
                <td style={cellStyle}>{d.hostname}</td>
                <td style={cellStyle}>{d.ultima_verificacao}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

const btnStyle = {
  padding: '12px 15px',
  fontSize: '1rem',
  border: '1px solid #bbb',
  borderRadius: '6px',
  cursor: 'pointer',
  transition: 'background-color 0.3s ease',
  textAlign: 'left'
};

const cellStyle = {
  border: '1px solid #ccc',
  padding: '8px',
  textAlign: 'left'
};

const infoCellLabel = {
  padding: '10px',
  fontWeight: 'bold',
  backgroundColor: '#f3f4f6',
  border: '1px solid #d1d5db',
  width: '120px'
};

const infoCellValue = {
  padding: '10px',
  backgroundColor: '#ffffff',
  border: '1px solid #d1d5db'
};

export default Dashboard;
