import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { ApiError } from "../services/apiClient";

export function Login() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("demo");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("demo123");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, fullName, password);
      }
      navigate("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="page-error">{error}</div>}
      <div className="form-row">
        <label htmlFor="email">Username</label>
        <input
          id="email"
          type="text"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoFocus
        />
      </div>
      {mode === "register" && (
        <div className="form-row">
          <label htmlFor="full_name">Full name</label>
          <input id="full_name" required value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </div>
      )}
      <div className="form-row">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          required
          minLength={6}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      <button className="btn" type="submit" disabled={submitting} style={{ width: "100%" }}>
        {submitting ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"}
      </button>
      <div className="auth-switch">
        {mode === "login" ? (
          <>
            No account?{" "}
            <button type="button" className="btn-link" onClick={() => setMode("register")}>
              Register
            </button>
          </>
        ) : (
          <>
            Already have an account?{" "}
            <button type="button" className="btn-link" onClick={() => setMode("login")}>
              Sign in
            </button>
          </>
        )}
      </div>
    </form>
  );
}
