import { useState, useEffect } from "react";
import { QRCodeSVG } from "qrcode.react";
import { useAuth } from "../contexts/AuthContext";
import { authApi } from "../api/auth";

const APPS_2FA = [
  { name: "Google Authenticator", url: "https://support.google.com/accounts/answer/1066447" },
  { name: "2FAS Authenticator", url: "https://2fas.com/" },
  { name: "Microsoft Authenticator", url: "https://www.microsoft.com/es-es/security/mobile-authenticator-app" },
  { name: "Authy", url: "https://authy.com/download/" },
];

export default function TwoFA() {
  const { getAccessToken } = useAuth();
  const [tiene2FA, setTiene2FA] = useState(false);
  const [setup, setSetup] = useState<{ secret: string; provisioning_uri: string } | null>(null);
  const [modalPaso, setModalPaso] = useState<1 | 2>(1);
  const [codigo, setCodigo] = useState("");
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const token = getAccessToken();

  useEffect(() => {
    if (!token) return;
    authApi.get2FAEstado(token).then((r) => setTiene2FA(r.tiene_2fa));
  }, [token]);

  const abrirModalSetup = async () => {
    if (!token) return;
    setError("");
    setCodigo("");
    setModalPaso(1);
    const data = await authApi.get2FASetup(token);
    setSetup(data);
  };

  const cerrarModal = () => {
    setSetup(null);
    setModalPaso(1);
    setCodigo("");
    setError("");
  };

  const continuarAVerificar = () => {
    setModalPaso(2);
  };

  const activar = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !setup) return;
    setError("");
    setLoading(true);
    try {
      const r = await authApi.activar2FA(token, setup.secret, codigo);
      setBackupCodes(r.backup_codes);
      setTiene2FA(true);
      cerrarModal();
      setSuccess("2FA activado. Guarda los códigos de respaldo.");
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Código inválido.");
    } finally {
      setLoading(false);
    }
  };

  const desactivar = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setError("");
    setLoading(true);
    try {
      await authApi.desactivar2FA(token, codigo);
      setTiene2FA(false);
      setCodigo("");
      setSuccess("2FA desactivado.");
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Código inválido.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ marginTop: "2rem" }}>
        <h1>Autenticación en dos pasos (2FA)</h1>
        <p>Estado: <strong>{tiene2FA ? "Activo" : "Inactivo"}</strong></p>

        {!tiene2FA && !setup && (
          <button type="button" className="btn btn-primary" onClick={abrirModalSetup}>
            Activar 2FA
          </button>
        )}

        {backupCodes.length > 0 && (
          <div style={{ marginTop: "1rem", padding: "1rem", background: "#f5f5f5", borderRadius: 4 }}>
            <strong>Códigos de respaldo (guárdalos en un lugar seguro):</strong>
            <ul>
              {backupCodes.map((c) => (
                <li key={c} style={{ fontFamily: "monospace" }}>{c}</li>
              ))}
            </ul>
            <button type="button" className="btn btn-secondary" onClick={() => setBackupCodes([])}>
              Ocultar
            </button>
          </div>
        )}

        {tiene2FA && !setup && (
          <form onSubmit={desactivar} style={{ marginTop: "1rem" }}>
            <div className="form-group">
              <label>Para desactivar 2FA, ingresa tu código actual</label>
              <input
                type="text"
                value={codigo}
                onChange={(e) => setCodigo(e.target.value)}
                placeholder="Código TOTP o de respaldo"
              />
            </div>
            {error && <p className="error">{error}</p>}
            {success && <p style={{ color: "green" }}>{success}</p>}
            <button type="submit" className="btn btn-secondary" disabled={loading}>
              Desactivar 2FA
            </button>
          </form>
        )}
      </div>

      {/* Modal Activar autenticación de dos factores */}
      {setup && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && cerrarModal()}>
          <div className="modal-2fa" onClick={(e) => e.stopPropagation()}>
            <button type="button" className="modal-2fa__close" onClick={cerrarModal} aria-label="Cerrar">
              ✕
            </button>
            <div className="modal-2fa__header">
              <div className="modal-2fa__icon" aria-hidden>
                ▣
              </div>
            </div>
            <h2 className="modal-2fa__title">Activar autenticación de dos factores</h2>
            <div className="modal-2fa__body">
              <p className="modal-2fa__text">
                Para terminar de activar la autenticación de dos factores, escanea el código QR o ingresa la clave de
                configuración en tu aplicación de autenticación.
              </p>

              <div className="modal-2fa__apps">
                <p className="modal-2fa__apps-title">
                  Te recomendamos tener instalada en tu celular una aplicación de autenticación, por ejemplo:
                </p>
                <div className="modal-2fa__apps-links">
                  {APPS_2FA.map((app) => (
                    <a key={app.name} href={app.url} target="_blank" rel="noopener noreferrer">
                      {app.name}
                    </a>
                  ))}
                </div>
                <p className="modal-2fa__apps-disclaimer">
                  Cada enlace se abre en una nueva pestaña para que puedas descargar la app.
                </p>
              </div>

              <div className="modal-2fa__qr">
                <QRCodeSVG value={setup.provisioning_uri} size={200} level="M" />
              </div>
              <p className="modal-2fa__secret-fallback">Clave manual: {setup.secret}</p>

              {modalPaso === 1 ? (
                <button type="button" className="modal-2fa__btn-continuar" onClick={continuarAVerificar}>
                  Continuar
                </button>
              ) : (
                <div className="modal-2fa__step2">
                  <form onSubmit={activar}>
                    <div className="form-group">
                      <label>Ingresa el código de 6 dígitos de tu app</label>
                      <input
                        type="text"
                        inputMode="numeric"
                        maxLength={6}
                        value={codigo}
                        onChange={(e) => setCodigo(e.target.value.replace(/\D/g, ""))}
                        placeholder="000000"
                        autoFocus
                      />
                    </div>
                    {error && <p className="error">{error}</p>}
                    <button
                      type="submit"
                      className="modal-2fa__btn-continuar"
                      disabled={loading || codigo.length !== 6}
                    >
                      {loading ? "Verificando..." : "Verificar y activar"}
                    </button>
                  </form>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
