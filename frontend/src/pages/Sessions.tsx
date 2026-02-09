import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { authApi, type Sesion } from "../api/auth";

export default function Sessions() {
  const { getAccessToken } = useAuth();
  const [sesiones, setSesiones] = useState<Sesion[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    const token = getAccessToken();
    if (!token) return;
    authApi.getSesiones(token).then(setSesiones).finally(() => setLoading(false));
  };

  useEffect(load, [getAccessToken]);

  const revocar = async (id: number) => {
    const token = getAccessToken();
    if (!token) return;
    await authApi.revocarSesion(token, id);
    load();
  };

  if (loading) return <div className="container card">Cargando sesiones...</div>;

  return (
    <div className="container">
      <div className="card" style={{ marginTop: "2rem" }}>
        <h1>Sesiones activas</h1>
        <p>Dispositivos donde has iniciado sesión. Puedes revocar una sesión para cerrarla en ese dispositivo.</p>
        <ul style={{ listStyle: "none", padding: 0 }}>
          {sesiones.map((s) => (
            <li key={s.id} style={{ padding: "0.75rem", borderBottom: "1px solid #eee", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div><strong>IP:</strong> {s.ip ?? "—"} | <strong>Última actividad:</strong> {new Date(s.ultima_actividad).toLocaleString()}</div>
                <div style={{ fontSize: "0.875rem", color: "#666" }}>{s.user_agent || "—"}</div>
              </div>
              <button type="button" className="btn btn-secondary" onClick={() => revocar(s.id)}>
                Cerrar sesión
              </button>
            </li>
          ))}
        </ul>
        {sesiones.length === 0 && <p>No hay sesiones registradas.</p>}
      </div>
    </div>
  );
}
