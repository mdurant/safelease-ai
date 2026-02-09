import { useAuth } from "../contexts/AuthContext";

export default function Dashboard() {
  const { state } = useAuth();
  const nombre = state.user?.perfil
    ? [state.user.perfil.nombre, state.user.perfil.apellido].filter(Boolean).join(" ") || state.user.email
    : state.user?.email;

  return (
    <div className="container">
      <div className="card" style={{ marginTop: "2rem" }}>
        <h1>Dashboard</h1>
        <p>Hola, <strong>{nombre}</strong>.</p>
        <p>Email verificado: {state.user?.verified_email ? "Sí" : "No"}</p>
        <p>Rol: {state.user?.rol_info?.nombre ?? "—"}</p>
        <p style={{ color: "#666", marginTop: "2rem" }}>
          Módulo 1 (Autenticación) listo. Próximamente: Mis Publicaciones, Pack de Avisos, etc.
        </p>
      </div>
    </div>
  );
}
