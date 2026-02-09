import { useState, useEffect } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { authApi } from "../api/auth";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("cr");
  const [status, setStatus] = useState<"idle" | "loading" | "ok" | "error">("idle");
  const [message, setMessage] = useState("");
  const [usuarioId, setUsuarioId] = useState<number | null>(null);

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Falta el token de verificación.");
      return;
    }
    setStatus("loading");
    authApi
      .verificarEmail(token)
      .then((data) => {
        setStatus("ok");
        setMessage(data.detail);
        setUsuarioId(data.usuario_id);
      })
      .catch((err) => {
        setStatus("error");
        setMessage((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Token inválido o expirado.");
      });
  }, [token]);

  if (status === "loading" || status === "idle") {
    return (
      <div className="container">
        <div className="card" style={{ marginTop: "2rem" }}>
          <p>Verificando correo...</p>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="container">
        <div className="card" style={{ marginTop: "2rem" }}>
          <h2>Error</h2>
          <p className="error">{message}</p>
          <p><Link to="/ingresar">Volver a ingresar</Link></p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card" style={{ marginTop: "2rem" }}>
        <h2>Correo verificado</h2>
        <p>{message}</p>
        <p>Revisa tu bandeja: te enviamos un código de 6 dígitos. Ingrésalo en la siguiente pantalla.</p>
        {usuarioId != null && (
          <p>
            <Link to={`/verificar-otp?usuario_id=${usuarioId}`}>Ir a ingresar código OTP</Link>
          </p>
        )}
      </div>
    </div>
  );
}
