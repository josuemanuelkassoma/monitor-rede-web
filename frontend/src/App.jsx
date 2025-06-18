// src/App.jsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './Layout/Layout';
import Dashboard from './pages/Dashboard';
import Dispositivos from './pages/Dispositivos';
import Speedtest from './pages/Speedtest';
import Trafego from './pages/Trafego';
import SessoesTrafego from './pages/SessoesTrafego';
import Historico from './pages/Historico';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="dispositivos" element={<Dispositivos />} />
        <Route path="speedtest" element={<Speedtest />} />
        <Route path="trafego" element={<Trafego />} />
        <Route path="sessoestrafego" element={<SessoesTrafego />} />
        <Route path="historico" element={<Historico />} />
      </Route>
    </Routes>
  );
}

export default App;
