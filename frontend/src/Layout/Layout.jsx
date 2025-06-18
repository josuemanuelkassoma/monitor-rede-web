import { NavLink, Outlet } from 'react-router-dom';
import './Layout.css'; // importa o CSS externo

export default function Layout() {
  return (
    <div>
      <header className="header">
        <h1 className="title">Monitor de Rede</h1>
        <nav className="nav">
          <NavLink to="/" end className="nav-link">Dashboard</NavLink>
          <NavLink to="/dispositivos" className="nav-link">Dispositivos</NavLink>
          <NavLink to="/speedtest" className="nav-link">Speedtest</NavLink>
          <NavLink to="/trafego" className="nav-link">Tráfego</NavLink>
          <NavLink to="/sessoestrafego" className="nav-link">SessõesTráfego</NavLink>
          <NavLink to="/historico" className="nav-link">Histórico</NavLink>
        </nav>
      </header>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
