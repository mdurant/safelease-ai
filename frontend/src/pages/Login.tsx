import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { authApi, isAuthError } from "../api/auth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err: unknown) {
      if (isAuthError(err) || (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail) {
        setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Credenciales incorrectas.");
      } else {
        setError("Error al conectar. Revisa que el backend esté en marcha.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ marginTop: "2rem" }}>
        <h1 style={{ marginTop: 0 }}>Ingresar</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <div className="form-group">
            <label>Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
        <p style={{ marginTop: "1rem" }}>
          ¿No tienes cuenta? <Link to="/registro">Crear cuenta</Link>
        </p>
        <p>
          <Link to="/restablecer-password">Olvidé mi contraseña</Link>
        </p>
      </div>
    </div>
  );
}
