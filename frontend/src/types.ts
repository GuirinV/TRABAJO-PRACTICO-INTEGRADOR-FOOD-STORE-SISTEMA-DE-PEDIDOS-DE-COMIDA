export type Usuario = {
  id: number
  nombre: string
  email: string
  rol: 'user' | 'admin'
  disabled: boolean
}

export type Categoria = { id: number; nombre: string; descripcion: string | null; activo: boolean }

export type Producto = {
  id: number
  nombre: string
  descripcion: string | null
  precio: number
  stock: number
  disponible: boolean
  activo: boolean
  categoria_id: number
}

export type ItemPedido = {
  id: number
  producto_id: number
  nombre_producto: string
  precio_unitario: number
  cantidad: number
  subtotal: number
}

export type Pedido = {
  id: number
  usuario_id: number
  estado: 'PENDIENTE' | 'EN_PREPARACION' | 'ENTREGADO' | 'CANCELADO'
  forma_pago: 'EFECTIVO' | 'TRANSFERENCIA'
  direccion_entrega: string
  total: number
  creado_en: string
  items: ItemPedido[]
}

export type Pagina<T> = { total: number; items: T[] }
