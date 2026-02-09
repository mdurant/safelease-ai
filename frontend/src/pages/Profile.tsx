import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { authApi, type Perfil } from "../api/auth";

export default function Profile() {
  const { state, getAccessToken, refreshUser } = useAuth();
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [telefono, setTelefono] = useState("");
  const [telefono_alternativo, setTelefonoAlternativo] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;
    authApi.getPerfil(token).then(setPerfil).catch(() => {});
  }, [state.user, getAccessToken]);

  useEffect(() => {
    if (perfil) {
      setNombre(perfil.nombre || "");
      setApellido(perfil.apellido || "");
      setTelefono(perfil.telefono || "");
      setTelefonoAlternativo(perfil.telefono_alternativo || "");
    }
  }, [perfil]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      await authApi.actualizarPerfil(token, {
        nombre,
        apellido,
        telefono,
        telefono_alternativo,
      });
      setSuccess("Perfil actualizado.");
      refreshUser();
    } catch {
      setError("Error al actualizar.");
    } finally {
      setLoading(false);
    }
  };

  const handleAvatar = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !getAccessToken()) return;
    try {
      const updated = await authApi.subirAvatar(getAccessToken()!, file);
      setPerfil(updated);
      refreshUser();
    } catch {
      setError("Error al subir avatar.");
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ marginTop: "2rem" }}>
        <h1>Perfil</h1>
        <p>Email: <strong>{state.user?.email}</strong></p>
        <div className="form-group">
          <label>Avatar</label>
          <input type="file" accept="image/*" onChange={handleAvatar} />
        </div>
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
            <label>Teléfono alternativo</label>
            <input type="tel" value={telefono_alternativo} onChange={(e) => setTelefonoAlternativo(e.target.value)} />
          </div>
          {error && <p className="error">{error}</p>}
          {success && <p style={{ color: "green" }}>{success}</p>}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Guardando..." : "Guardar"}
          </button>
        </form>
      </div>
    </div>
  );
}
