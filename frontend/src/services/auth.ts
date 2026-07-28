import { api, clearToken, setToken } from "./apiClient";
import type { User } from "../types";

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const authService = {
  async login(email: string, password: string): Promise<User> {
    const { access_token } = await api.post<TokenResponse>("/auth/login", { email, password });
    setToken(access_token);
    return authService.me();
  },

  register(email: string, full_name: string, password: string): Promise<User> {
    return api.post<User>("/auth/register", { email, full_name, password });
  },

  me(): Promise<User> {
    return api.get<User>("/auth/me");
  },

  logout(): void {
    clearToken();
  },
};
