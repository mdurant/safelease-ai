import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";
import VerifyOTP from "./pages/VerifyOTP";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import ChangePassword from "./pages/ChangePassword";
import Sessions from "./pages/Sessions";
import TwoFA from "./pages/TwoFA";
import RestorePassword from "./pages/RestorePassword";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { state } = useAuth();
  if (state.loading) return <div className="container card">Cargando...</div>;
  if (!state.access) return <Navigate to="/ingresar" replace />;
  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { state } = useAuth();
  if (state.loading) return <div className="container card">Cargando...</div>;
  if (state.access && state.user) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/ingresar" element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/registro" element={<PublicRoute><Register /></PublicRoute>} />
      <Route path="/verificar-email" element={<VerifyEmail />} />
      <Route path="/verificar-otp" element={<VerifyOTP />} />
      <Route path="/restablecer-password" element={<RestorePassword />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="perfil" element={<PrivateRoute><Profile /></PrivateRoute>} />
        <Route path="cambiar-password" element={<PrivateRoute><ChangePassword /></PrivateRoute>} />
        <Route path="sesiones" element={<PrivateRoute><Sessions /></PrivateRoute>} />
        <Route path="2fa" element={<PrivateRoute><TwoFA /></PrivateRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
