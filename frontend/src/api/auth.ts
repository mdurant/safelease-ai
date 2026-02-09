/**
 * Cliente API de autenticación (módulo 1).
 * Base URL vía proxy Vite: /api -> FastAPI -> Django
 */
import axios, { AxiosError } from "axios";

const client = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

export interface Tokens {
  access: string;
  refresh: string;
  access_expires?: number;
  user_id: number;
  email: string;
  rol: string | null;
}

export interface User {
  id: number;
  email: string;
  verified_email: boolean;
  verified_phone: boolean;
  date_joined: string;
  rol: number | null;
  rol_info: { codigo: string; nombre: string } | null;
  perfil: Perfil | null;
}

export interface Perfil {
  id: number;
  nombre: string;
  apellido: string;
  telefono: string;
  telefono_alternativo: string;
  avatar: string | null;
  creado_en: string;
  actualizado_en: string;
}

export const authApi = {
  async registro(data: {
    email: string;
    password: string;
    password_confirm: string;
    nombre?: string;
    apellido?: string;
    telefono?: string;
    aceptar_terminos: boolean;
  }) {
    const r = await client.post<{ detail: string; email: string }>("/auth/registro/", data);
    return r.data;
  },

  async login(email: string, password: string) {
    const r = await client.post<Tokens>("/auth/login/", { email, password });
    return r.data;
  },

  async verificarEmail(token: string) {
    const r = await client.post<{ detail: string; usuario_id: number; email: string }>(
      "/auth/verificar-email/",
      { token }
    );
    return r.data;
  },

  async verificarOTP(usuario_id: number, codigo: string) {
    const r = await client.post<Tokens>("/auth/verificar-otp/", { usuario_id, codigo });
    return r.data;
  },

  async refreshToken(refresh: string) {
    const r = await client.post<{ access: string }>("/auth/token/refresh/", { refresh });
    return r.data;
  },

  async me(accessToken: string) {
    const r = await client.get<User>("/auth/me/", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    return r.data;
  },

  async solicitarRestablecerPassword(email: string) {
    const r = await client.post<{ detail: string }>("/auth/restablecer-password/solicitar/", {
      email,
    });
    return r.data;
  },

  async restablecerPassword(token: string, nueva_password: string, nueva_password_confirm: string) {
    const r = await client.post<{ detail: string }>("/auth/restablecer-password/", {
      token,
      nueva_password,
      nueva_password_confirm,
    });
    return r.data;
  },

  async cambiarPassword(accessToken: string, password_actual: string, nueva_password: string, nueva_password_confirm: string) {
    const r = await client.post<{ detail: string }>(
      "/auth/cambiar-password/",
      { password_actual, nueva_password, nueva_password_confirm },
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    return r.data;
  },

  async getPerfil(accessToken: string) {
    const r = await client.get<Perfil>("/auth/perfil/", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    return r.data;
  },

  async actualizarPerfil(accessToken: string, data: Partial<Perfil>) {
    const r = await client.patch<Perfil>("/auth/perfil/actualizar/", data, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    return r.data;
  },

  async subirAvatar(accessToken: string, file: File) {
    const form = new FormData();
    form.append("avatar", file);
    const r = await client.post<Perfil>("/auth/perfil/avatar/", form, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "multipart/form-data",
      },
    });
    return r.data;
  },

  async getSesiones(accessToken: string) {
    const r = await client.get<Sesion[]>("/auth/sesiones/", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    return r.data;
  },

  async revocarSesion(accessToken: string, id: number) {
    await client.post(`/auth/sesiones/${id}/revocar/`, {}, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
  },

  async get2FAEstado(accessToken: string) {
    const r = await client.get<{ tiene_2fa: boolean }>("/auth/2fa/estado/", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    return r.data;
  },

  async get2FASetup(accessToken: string) {
    const r = await client.get<{ secret: string; provisioning_uri: string }>(
      "/auth/2fa/setup/",
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    return r.data;
  },

  async activar2FA(accessToken: string, secret: string, codigo: string) {
    const r = await client.post<{ detail: string; backup_codes: string[] }>(
      "/auth/2fa/activar/",
      { secret, codigo },
      { headers: { Authorization: `Bearer ${accessToken}` } }
    );
    return r.data;
  },

  async desactivar2FA(accessToken: string, codigo: string) {
    const r = await client.post<{ detail: string }>("/auth/2fa/desactivar/", { codigo }, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    return r.data;
  },
};

export interface Sesion {
  id: number;
  device_id: string;
  ip: string | null;
  user_agent: string;
  ultima_actividad: string;
  creado_en: string;
}

export function isAuthError(e: unknown): boolean {
  return axios.isAxiosError(e) && (e as AxiosError).response?.status === 401;
}
