import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { authApi } from "../api/auth";

export default function ChangePassword() {
  const [password_actual, setPasswordActual] = useState("");
  const [nueva_password, setNuevaPassword] = useState("");
  const [nueva_password_confirm, setNuevaPasswordConfirm] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const { getAccessToken } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (nueva_password !== nueva_password_confirm) {
      setError("Las contraseñas nuevas no coinciden.");
      return;
    }
    const token = getAccessToken();
    if (!token) return;
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      await authApi.cambiarPassword(token, password_actual, nueva_password, nueva_password_confirm);
      setSuccess("Contraseña actualizada.");
      setPasswordActual("");
      setNuevaPassword("");
      setNuevaPasswordConfirm("");
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Error al cambiar contraseña.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ marginTop: "2rem" }}>
        <h1>Cambiar contraseña</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Contraseña actual</label>
            <input
              type="password"
              value={password_actual}
              onChange={(e) => setPasswordActual(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Nueva contraseña</label>
            <input
              type="password"
              value={nueva_password}
              onChange={(e) => setNuevaPassword(e.target.value)}
              required
              minLength={8}
            />
          </div>
          <div className="form-group">
            <label>Confirmar nueva contraseña</label>
            <input
              type="password"
              value={nueva_password_confirm}
              onChange={(e) => setNuevaPasswordConfirm(e.target.value)}
              required
            />
          </div>
          {error && <p className="error">{error}</p>}
          {success && <p style={{ color: "green" }}>{success}</p>}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Guardando..." : "Cambiar contraseña"}
          </button>
        </form>
      </div>
    </div>
  );
}
