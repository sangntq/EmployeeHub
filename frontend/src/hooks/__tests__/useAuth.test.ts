/**
 * useAuth フックのユニットテスト
 *
 * テスト対象:
 *   - hasRole, isAdmin, isManager, canSearch, canApprove, canViewDashboard
 */
import { beforeEach, describe, expect, it } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useAuthStore } from '../../stores/authStore'
import { useAuth } from '../useAuth'
import type { AuthUser, SystemRole } from '../../types'

// ── ヘルパー ───────────────────────────────────────────────────────────────────

function makeUser(role: SystemRole): AuthUser {
  return {
    id: 'user-001',
    email: `${role}@test.local`,
    name: `テスト ${role}`,
    employeeId: 'emp-001',
    systemRole: role,
  }
}

function setStoreUser(role: SystemRole) {
  act(() => {
    useAuthStore.setState({
      user: makeUser(role),
      accessToken: 'dummy-token',
      isAuthenticated: true,
    })
  })
}

// ── セットアップ ───────────────────────────────────────────────────────────────

beforeEach(() => {
  act(() => {
    useAuthStore.setState({ user: null, accessToken: null, isAuthenticated: false })
  })
})

// ── テスト ────────────────────────────────────────────────────────────────────

describe('isAdmin', () => {
  it('admin ロールは true を返す', () => {
    setStoreUser('admin')
    const { result } = renderHook(() => useAuth())
    expect(result.current.isAdmin()).toBe(true)
  })

  it('member ロールは false を返す', () => {
    setStoreUser('member')
    const { result } = renderHook(() => useAuth())
    expect(result.current.isAdmin()).toBe(false)
  })
})

describe('isManager', () => {
  it.each(['manager', 'department_head', 'director', 'admin'] as SystemRole[])(
    '%s ロールは true を返す',
    (role) => {
      setStoreUser(role)
      const { result } = renderHook(() => useAuth())
      expect(result.current.isManager()).toBe(true)
    },
  )

  it.each(['member', 'sales'] as SystemRole[])('%s ロールは false を返す', (role) => {
    setStoreUser(role)
    const { result } = renderHook(() => useAuth())
    expect(result.current.isManager()).toBe(false)
  })
})

describe('canSearch', () => {
  it.each(['sales', 'manager', 'department_head', 'director', 'admin'] as SystemRole[])(
    '%s ロールは検索可能',
    (role) => {
      setStoreUser(role)
      const { result } = renderHook(() => useAuth())
      expect(result.current.canSearch()).toBe(true)
    },
  )

  it('member ロールは検索不可', () => {
    setStoreUser('member')
    const { result } = renderHook(() => useAuth())
    expect(result.current.canSearch()).toBe(false)
  })
})

describe('canApprove', () => {
  it.each(['manager', 'department_head', 'admin'] as SystemRole[])(
    '%s ロールは承認可能',
    (role) => {
      setStoreUser(role)
      const { result } = renderHook(() => useAuth())
      expect(result.current.canApprove()).toBe(true)
    },
  )

  it.each(['member', 'sales', 'director'] as SystemRole[])(
    '%s ロールは承認不可',
    (role) => {
      setStoreUser(role)
      const { result } = renderHook(() => useAuth())
      expect(result.current.canApprove()).toBe(false)
    },
  )
})

describe('未認証', () => {
  it('isAdmin は false を返す', () => {
    const { result } = renderHook(() => useAuth())
    expect(result.current.isAdmin()).toBe(false)
    expect(result.current.isAuthenticated).toBe(false)
  })
})
