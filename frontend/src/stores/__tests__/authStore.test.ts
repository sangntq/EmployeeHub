/**
 * authStore のユニットテスト
 *
 * テスト対象:
 *   - setAuth: 認証情報をストアと localStorage に保存する
 *   - logout: 認証情報を消去する
 *   - updateUser: ユーザー情報を部分更新する
 */
import { beforeEach, describe, expect, it } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useAuthStore } from '../authStore'
import type { AuthUser } from '../../types'

// ── テストデータ ───────────────────────────────────────────────────────────────

const mockUser: AuthUser = {
  id: 'user-001',
  email: 'admin@test.local',
  name: 'テスト管理者',
  employeeId: 'emp-001',
  systemRole: 'admin',
  avatarUrl: undefined,
}

// ── セットアップ ───────────────────────────────────────────────────────────────

beforeEach(() => {
  // 各テスト前にストアと localStorage を初期状態に戻す
  act(() => {
    useAuthStore.setState({
      user: null,
      accessToken: null,
      isAuthenticated: false,
    })
  })
  localStorage.clear()
})

// ── テスト ────────────────────────────────────────────────────────────────────

describe('setAuth', () => {
  it('ストアにユーザー情報とトークンを保存する', () => {
    const { result } = renderHook(() => useAuthStore())

    act(() => {
      result.current.setAuth(mockUser, 'access-token-xyz', 'refresh-token-xyz')
    })

    expect(result.current.user).toEqual(mockUser)
    expect(result.current.accessToken).toBe('access-token-xyz')
    expect(result.current.isAuthenticated).toBe(true)
  })

  it('localStorage にトークンを書き込む', () => {
    const { result } = renderHook(() => useAuthStore())

    act(() => {
      result.current.setAuth(mockUser, 'access-aaa', 'refresh-bbb')
    })

    expect(localStorage.getItem('access_token')).toBe('access-aaa')
    expect(localStorage.getItem('refresh_token')).toBe('refresh-bbb')
  })
})

describe('logout', () => {
  it('ストアを初期状態に戻す', () => {
    const { result } = renderHook(() => useAuthStore())

    act(() => {
      result.current.setAuth(mockUser, 'access-token', 'refresh-token')
    })
    act(() => {
      result.current.logout()
    })

    expect(result.current.user).toBeNull()
    expect(result.current.accessToken).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('localStorage のトークンを削除する', () => {
    const { result } = renderHook(() => useAuthStore())

    act(() => {
      result.current.setAuth(mockUser, 'access-token', 'refresh-token')
    })
    act(() => {
      result.current.logout()
    })

    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })
})

describe('updateUser', () => {
  it('ユーザー情報を部分更新する', () => {
    const { result } = renderHook(() => useAuthStore())

    act(() => {
      result.current.setAuth(mockUser, 'access-token', 'refresh-token')
    })
    act(() => {
      result.current.updateUser({ name: '更新済み管理者', avatarUrl: 'https://example.com/avatar.png' })
    })

    expect(result.current.user?.name).toBe('更新済み管理者')
    expect(result.current.user?.avatarUrl).toBe('https://example.com/avatar.png')
    // 変更していないフィールドは保持される
    expect(result.current.user?.systemRole).toBe('admin')
    expect(result.current.user?.email).toBe('admin@test.local')
  })

  it('未認証状態では user が null のまま', () => {
    const { result } = renderHook(() => useAuthStore())

    act(() => {
      result.current.updateUser({ name: '誰でもない' })
    })

    expect(result.current.user).toBeNull()
  })
})
