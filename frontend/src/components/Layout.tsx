import { Outlet, Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Layout() {
  const { state, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/ingresar");
  };

  return (
    <div>
      {state.access && (
        <nav className="nav">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/perfil">Perfil</Link>
          <Link to="/cambiar-password">Contraseña</Link>
          <Link to="/sesiones">Sesiones</Link>
          <Link to="/2fa">2FA</Link>
          <span style={{ marginLeft: "auto" }}>
            {state.user?.email}
            <button type="button" className="btn btn-secondary" style={{ marginLeft: "0.5rem" }} onClick={handleLogout}>
              Salir
            </button>
          </span>
        </nav>
      )}
      <main>
        <Outlet />
      </main>
    </div>
  );
}
