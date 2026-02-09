import { useState } from "react";
import { Link } from "react-router-dom";
import { authApi } from "../api/auth";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password_confirm, setPasswordConfirm] = useState("");
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [telefono, setTelefono] = useState("");
  const [aceptar, setAceptar] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (password !== password_confirm) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    if (!aceptar) {
      setError("Debes aceptar los términos y condiciones.");
      return;
    }
    setLoading(true);
    try {
      await authApi.registro({
        email,
        password,
        password_confirm,
        nombre,
        apellido,
        telefono: telefono || undefined,
        aceptar_terminos: true,
      });
      setSuccess(true);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string; email?: string[] } } })?.response?.data;
      setError(typeof msg?.detail === "string" ? msg.detail : msg?.email?.[0] || "Error al crear la cuenta.");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="container">
        <div className="card" style={{ marginTop: "2rem" }}>
          <h2>Cuenta creada</h2>
          <p>Te enviamos un correo a <strong>{email}</strong> para verificar y activar tu cuenta.</p>
          <p>Revisa tu bandeja (y spam) y haz clic en el enlace del correo.</p>
          <p><Link to="/ingresar">Ir a ingresar</Link></p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card" style={{ marginTop: "2rem" }}>
        <h1 style={{ marginTop: 0 }}>Crear cuenta</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Nombre</label>
            <input value={nombre} onChange={(e) => setNombre(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Apellido</label>
            <input value={apellido} onChange={(e) => setApellido(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Teléfono</label>
            <input type="tel" value={telefono} onChange={(e) => setTelefono(e.target.value)} />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Contraseña</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
          </div>
          <div className="form-group">
            <label>Confirmar contraseña</label>
            <input type="password" value={password_confirm} onChange={(e) => setPasswordConfirm(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>
              <input type="checkbox" checked={aceptar} onChange={(e) => setAceptar(e.target.checked)} />
              Acepto términos y condiciones
            </label>
          </div>
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Creando..." : "Crear cuenta"}
          </button>
        </form>
        <p style={{ marginTop: "1rem" }}>
          ¿Ya tienes cuenta? <Link to="/ingresar">Ingresar</Link>
        </p>
      </div>
    </div>
  );
}
