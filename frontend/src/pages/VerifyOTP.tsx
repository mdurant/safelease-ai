import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { authApi } from "../api/auth";
import { useAuth } from "../contexts/AuthContext";

export default function VerifyOTP() {
  const [searchParams] = useSearchParams();
  const usuarioIdParam = searchParams.get("usuario_id");
  const usuarioId = usuarioIdParam ? parseInt(usuarioIdParam, 10) : null;
  const [codigo, setCodigo] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { setTokens } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!usuarioId || codigo.length !== 6) {
      setError("Ingresa el código de 6 dígitos.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const tokens = await authApi.verificarOTP(usuarioId, codigo);
      setTokens(tokens);
      navigate("/dashboard");
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Código inválido o expirado.");
    } finally {
      setLoading(false);
    }
  };

  if (!usuarioId) {
    return (
      <div className="container">
        <div className="card" style={{ marginTop: "2rem" }}>
          <p>Falta el identificador de usuario. Completa la verificación desde el enlace del correo.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card" style={{ marginTop: "2rem" }}>
        <h2>Código de verificación</h2>
        <p>Ingresa los 6 dígitos que te enviamos por correo.</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Código (6 dígitos)</label>
            <input
              type="text"
              inputMode="numeric"
              maxLength={6}
              value={codigo}
              onChange={(e) => setCodigo(e.target.value.replace(/\D/g, ""))}
              placeholder="000000"
            />
          </div>
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn btn-primary" disabled={loading || codigo.length !== 6}>
            {loading ? "Verificando..." : "Validar"}
          </button>
        </form>
      </div>
    </div>
  );
}
