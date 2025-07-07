import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend);

function Historico() {
  const [tipoSelecionado, setTipoSelecionado] = useState('dispositivos');
  const [dados, setDados] = useState([]);
  const [periodo, setPeriodo] = useState('todos');
  const API_URL = "https://mynetwork-egj2.onrender.com";

  useEffect(() => {
    buscarHistorico(tipoSelecionado);
  }, [tipoSelecionado]);

  const buscarHistorico = async (tipo) => {
    let url = '';
    switch (tipo) {
      case 'dispositivos':
       url = `${API_URL}/devices/db`;
        break;
      case 'speedtest':
       url = `${API_URL}/speedtest/historico`;
        break;
      case 'trafego':
        url = `${API_URL}/trafego/historico`;
        break;
      case 'sessoes':
        url = `${API_URL}/trafego/sessoes`;
        break;
    }

    try {
      const res = await axios.get(url);
      let registros = [];

      if (tipo === 'dispositivos') {
        registros = res.data.dispositivos.map(d => ({
          ip: d.ip,
          mac: d.mac,
          hostname: d.hostname,
          tipo: d.tipo,
          fabricante: d.fabricante,
          ultima_verificacao: d.ultima_verificacao,
          online: d.online ? 'Sim' : 'Não'
        }));
      } else if (tipo === 'sessoes') {
        registros = res.data.sessoes.map(s => ({
          inicio: s.inicio,
          fim: s.fim,
          download_usado_mb: s.download_usado_mb,
          upload_usado_mb: s.upload_usado_mb,
          total_usado_mb: s.total_usado_mb
        }));
      } else if (tipo === 'speedtest') {
        registros = res.data.historico.map(s => ({
          data: s.timestamp,
          download_mb: s.download_mb,
          upload_mb: s.upload_mb,
          total_mb: (s.download_mb + s.upload_mb).toFixed(2),
          ping_ms: s.ping_ms
        }));
      } else if (tipo === 'trafego') {
        registros = res.data.historico.map(t => ({
          data: t.timestamp,
          download_mb: t.download_mb,
          upload_mb: t.upload_mb,
          total_mb: (t.download_mb + t.upload_mb).toFixed(2)
        }));
      }

      setDados(registros);
    } catch (error) {
      console.error('Erro ao buscar histórico:', error);
    }
  };

  const limparHistorico = async () => {
    const confirmacao = window.confirm(`Tem certeza que deseja apagar o histórico de ${tipoSelecionado}?`);
    if (!confirmacao) return;
  
    let rota = '';
    switch (tipoSelecionado) {
      case 'dispositivos':
        rota = '/deletar/dispositivos';
        break;
      case 'sessoes':
        rota = '/deletar/sessoes';
        break;
      case 'speedtest':
        rota = '/deletar/speedtest';
        break;
      case 'trafego':
        rota = '/deletar/trafego';
        break;
    }
  
    try {
      await axios.delete(`${API_URL}${rota}`);
      alert(`Histórico de ${tipoSelecionado} apagado com sucesso.`);
      buscarHistorico(tipoSelecionado);
    } catch (error) {
      alert("Erro ao apagar os dados.");
      console.error(error);
    }
  };
  

  const filtrarPorPeriodo = (lista) => {
    if (periodo === 'todos') return lista;

    const agora = new Date();
    const limites = {
      '5min': 5 * 60 * 1000,
      '30min': 30 * 60 * 1000,
      '1h': 60 * 60 * 1000,
      '1semana': 7 * 24 * 60 * 60 * 1000,
      '1mes': 30 * 24 * 60 * 60 * 1000,
    };

    const limite = limites[periodo];
    return lista.filter(item => {
      const ts = new Date(item.timestamp || item.inicio || item.ultima_verificacao || item.data);
      return agora - ts <= limite;
    });
  };

  const gerarDataset = () => {
    const filtrado = filtrarPorPeriodo(dados);
    const labels = filtrado.map(d => d.timestamp || d.inicio || d.ultima_verificacao || d.data);

    switch (tipoSelecionado) {
      case 'speedtest':
        return {
          labels,
          datasets: [
            {
              label: 'Download (Mbps)',
              data: filtrado.map(d => d.download_mb),
              borderColor: 'blue',
              backgroundColor: 'rgba(0,0,255,0.2)'
            },
            {
              label: 'Upload (Mbps)',
              data: filtrado.map(d => d.upload_mb),
              borderColor: 'green',
              backgroundColor: 'rgba(0,255,0,0.2)'
            },
            {
              label: 'Ping (ms)',
              data: filtrado.map(d => d.ping_ms),
              borderColor: 'gray',
              backgroundColor: 'rgba(128,128,128,0.2)'
            }
          ]
        };
      case 'trafego':
        return {
          labels,
          datasets: [
            {
              label: 'Download (MB)',
              data: filtrado.map(d => d.download_mb),
              borderColor: 'blue'
            },
            {
              label: 'Upload (MB)',
              data: filtrado.map(d => d.upload_mb),
              borderColor: 'green'
            },
            {
              label: 'Total (MB)',
              data: filtrado.map(d => d.total_mb),
              borderColor: 'orange'
            }
          ]
        };
      case 'sessoes':
        return {
          labels,
          datasets: [
            {
              label: 'Download Usado (MB)',
              data: filtrado.map(d => d.download_usado_mb),
              borderColor: 'blue'
            },
            {
              label: 'Upload Usado (MB)',
              data: filtrado.map(d => d.upload_usado_mb),
              borderColor: 'green'
            },
            {
              label: 'Total Usado (MB)',
              data: filtrado.map(d => d.total_usado_mb),
              borderColor: 'orange'
            }
          ]
        };
      case 'dispositivos':
        return {
          labels,
          datasets: [
            {
              label: 'Dispositivos Registrados',
              data: filtrado.map((_, i) => i + 1),
              borderColor: 'purple',
              backgroundColor: 'rgba(128,0,128,0.2)'
            }
          ]
        };
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '1rem' }}>Histórico de Monitoramento</h1>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <button onClick={() => setTipoSelecionado('dispositivos')} style={botao(tipoSelecionado === 'dispositivos')}>Dispositivos</button>
        <button onClick={() => setTipoSelecionado('sessoes')} style={botao(tipoSelecionado === 'sessoes')}>Sessões de Tráfego</button>
        <button onClick={() => setTipoSelecionado('speedtest')} style={botao(tipoSelecionado === 'speedtest')}>Speedtest</button>
        <button onClick={() => setTipoSelecionado('trafego')} style={botao(tipoSelecionado === 'trafego')}>Tráfego</button>

        <button onClick={limparHistorico} style={botaoExcluir}>🗑 Limpar</button>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <label>Filtrar por período: </label>
        <select onChange={e => setPeriodo(e.target.value)} value={periodo}>
          <option value="todos">Todos</option>
          <option value="5min">Últimos 5 minutos</option>
          <option value="30min">Últimos 30 minutos</option>
          <option value="1h">Última hora</option>
          <option value="1semana">Última semana</option>
          <option value="1mes">Último mês</option>
        </select>
      </div>

      <div style={{ overflowX: 'auto', marginBottom: '2rem' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.95rem' }}>
          <thead style={{ backgroundColor: '#f0f0f0' }}>
            <tr>
              {dados.length > 0 &&
                Object.keys(dados[0]).map((k, i) => (
                  <th key={i} style={cellHeaderStyle}>{k.replace(/_/g, ' ').toUpperCase()}</th>
                ))}
            </tr>
          </thead>
          <tbody>
            {filtrarPorPeriodo(dados).map((dado, i) => (
              <tr key={i}>
                {Object.values(dado).map((v, j) => (
                  <td key={j} style={cellStyle}>{String(v)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ maxWidth: '800px', margin: 'auto' }}>
        <h3 style={{ textAlign: 'center', marginBottom: '1rem' }}>Gráfico de Linha</h3>
        <Line data={gerarDataset()} options={{ responsive: true }} />
      </div>
    </div>
  );
}

const botao = (ativo) => ({
  padding: '10px 20px',
  backgroundColor: ativo ? '#2563eb' : '#e5e7eb',
  color: ativo ? 'white' : '#111827',
  border: 'none',
  borderRadius: '6px',
  cursor: 'pointer',
  fontWeight: 'bold',
});

const botaoExcluir = {
  padding: '10px 20px',
  backgroundColor: '#dc2626',
  color: 'white',
  border: 'none',
  borderRadius: '6px',
  cursor: 'pointer',
  fontWeight: 'bold',
};

const cellStyle = {
  border: '1px solid #ccc',
  padding: '8px',
  textAlign: 'left'
};

const cellHeaderStyle = {
  ...cellStyle,
  fontWeight: 'bold',
  backgroundColor: '#e2e8f0'
};

export default Historico;
