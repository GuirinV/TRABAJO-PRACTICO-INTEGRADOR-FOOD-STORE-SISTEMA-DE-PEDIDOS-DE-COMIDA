import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'

type CartLine = { producto_id: number; nombre: string; precio: number; cantidad: number }
type CartState = {
  items: CartLine[]
  agregar: (linea: Omit<CartLine, 'cantidad'>) => void
  cambiarCantidad: (productoId: number, cantidad: number) => void
  quitar: (productoId: number) => void
  limpiar: () => void
}

export const useCartStore = create<CartState>()(
  persist(
    (set) => ({
      items: [],
      agregar: (linea) => set((state) => {
        const existente = state.items.find((item) => item.producto_id === linea.producto_id)
        if (existente) {
          return { items: state.items.map((item) => item.producto_id === linea.producto_id ? { ...item, cantidad: item.cantidad + 1 } : item) }
        }
        return { items: [...state.items, { ...linea, cantidad: 1 }] }
      }),
      cambiarCantidad: (productoId, cantidad) => set((state) => ({
        items: cantidad < 1 ? state.items.filter((item) => item.producto_id !== productoId) : state.items.map((item) => item.producto_id === productoId ? { ...item, cantidad } : item),
      })),
      quitar: (productoId) => set((state) => ({ items: state.items.filter((item) => item.producto_id !== productoId) })),
      limpiar: () => set({ items: [] }),
    }),
    { name: 'food-store-cart', storage: createJSONStorage(() => localStorage) },
  ),
)
