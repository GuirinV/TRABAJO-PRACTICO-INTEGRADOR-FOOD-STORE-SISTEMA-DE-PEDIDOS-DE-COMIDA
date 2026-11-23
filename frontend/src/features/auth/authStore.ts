import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import type { Usuario } from '../../types'

type AuthState = {
  user: Usuario | null
  initialized: boolean
  setUser: (user: Usuario | null) => void
  setInitialized: (initialized: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      initialized: false,
      setUser: (user) => set({ user }),
      setInitialized: (initialized) => set({ initialized }),
    }),
    {
      name: 'food-store-user',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ user: state.user, initialized: state.initialized }),
    },
  ),
)
