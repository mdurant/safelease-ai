import { useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { authApi } from "../api/auth";

export default function RestorePassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password_confirm, setPasswordConfirm] = useState("");
  const [step, setStep] = useState<"solicitar" | "restablecer" | "ok">(token ? "restablecer" : "solicitar");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSolicitar = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authApi.solicitarRestablecerPassword(email);
      setStep("ok");
    } catch {
      setError("Error al enviar. Intenta de nuevo.");
    } finally {
      setLoading(false);
    }
  };

  const handleRestablecer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || password !== password_confirm) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await authApi.restablecerPassword(token, password, password_confirm);
      setStep("ok");
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Token inválido o expirado.");
    } finally {
      setLoading(false);
    }
  };

  if (step === "ok") {
    return (
      <div className="container">
        <div className="card" style={{ marginTop: "2rem" }}>
          <h2>Listo</h2>
          {token ? (
            <p>Contraseña actualizada. Ya puedes <Link to="/ingresar">iniciar sesión</Link>.</p>
          ) : (
            <p>Si el correo existe, recibirás un enlace para restablecer la contraseña.</p>
          )}
          <p><Link to="/ingresar">Volver a ingresar</Link></p>
        </div>
      </div>
    );
  }

  if (token) {
    return (
      <div className="container">
        <div className="card" style={{ marginTop: "2rem" }}>
          <h1>Nueva contraseña</h1>
          <form onSubmit={handleRestablecer}>
            <div className="form-group">
              <label>Nueva contraseña</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
            </div>
            <div className="form-group">
              <label>Confirmar contraseña</label>
              <input type="password" value={password_confirm} onChange={(e) => setPasswordConfirm(e.target.value)} required />
            </div>
            {error && <p className="error">{error}</p>}
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Guardando..." : "Restablecer contraseña"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card" style={{ marginTop: "2rem" }}>
        <h1>Olvidé mi contraseña</h1>
        <p>Ingresa tu email y te enviaremos un enlace para restablecerla.</p>
        <form onSubmit={handleSolicitar}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Enviando..." : "Enviar enlace"}
          </button>
        </form>
        <p style={{ marginTop: "1rem" }}><Link to="/ingresar">Volver a ingresar</Link></p>
      </div>
    </div>
  );
}
