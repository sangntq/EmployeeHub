import apiClient from './client'

export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  employee: {
    id: string
    employee_number: string
    name_ja: string
    name_en: string | null
    system_role: string
    avatar_url: string | null
  }
}

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<TokenResponse>('/auth/login', data).then(r => r.data),

  googleLogin: (idToken: string) =>
    apiClient.post<TokenResponse>('/auth/google', { id_token: idToken }).then(r => r.data),

  refresh: (refreshToken: string) =>
    apiClient
      .post<{ access_token: string; token_type: string }>('/auth/refresh', {
        refresh_token: refreshToken,
      })
      .then(r => r.data),

  logout: () => apiClient.delete('/auth/logout'),

  me: () => apiClient.get('/auth/me').then(r => r.data),
}
