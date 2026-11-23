import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { flexRender, getCoreRowModel, useReactTable, type ColumnDef } from '@tanstack/react-table'
import { api } from '../../api/client'
import type { Categoria, Pagina, Pedido, Producto, Usuario } from '../../types'

type Resumen = { pendientes: number; en_preparacion: number; entregados: number; cancelados: number; total_pedidos: number }
type Tab = 'resumen' | 'productos' | 'categorias' | 'pedidos' | 'usuarios'

function ProductTable({
  products,
  busy,
  perform,
}: {
  products: Producto[]
  busy: boolean
  perform: (action: () => Promise<unknown>) => void
}) {
  const columns: ColumnDef<Producto, unknown>[] = [
    { accessorKey: 'nombre', header: 'Producto' },
    { accessorKey: 'precio', header: 'Precio', cell: ({ getValue }) => `$${Number(getValue()).toFixed(2)}` },
    { accessorKey: 'stock', header: 'Stock' },
    { accessorKey: 'disponible', header: 'Disponible', cell: ({ getValue }) => getValue() ? 'Sí' : 'No' },
    {
      id: 'acciones',
      header: 'Acciones',
      cell: ({ row }) => {
        const product = row.original
        return <div className="actions">
          <button onClick={() => perform(() => api.patch(`/productos/${product.id}/estado`, { stock: product.stock + 1 }))} disabled={busy}>+ stock</button>
          <button onClick={() => perform(() => api.patch(`/productos/${product.id}/estado`, { disponible: !product.disponible }))} disabled={busy}>{product.disponible ? 'Pausar' : 'Habilitar'}</button>
          <button onClick={() => {
            const nombre = window.prompt('Nombre del producto', product.nombre)
            if (nombre === null || nombre.trim() === '') return
            const precioTexto = window.prompt('Precio', String(product.precio))
            if (precioTexto === null) return
            const precio = Number(precioTexto)
            if (!Number.isFinite(precio) || precio <= 0) return
            perform(() => api.put(`/productos/${product.id}`, { nombre: nombre.trim(), precio }))
          }} disabled={busy}>Editar</button>
          <button className="danger" onClick={() => perform(() => api.delete(`/productos/${product.id}`))} disabled={busy}>Dar de baja</button>
        </div>
      },
    },
  ]
  const table = useReactTable({ data: products, columns, getCoreRowModel: getCoreRowModel() })
  return <div className="admin-table-wrap"><table className="admin-table">
    <thead>{table.getHeaderGroups().map((group) => <tr key={group.id}>{group.headers.map((header) => <th key={header.id}>{header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}</th>)}</tr>)}</thead>
    <tbody>{table.getRowModel().rows.map((row) => <tr key={row.id}>{row.getVisibleCells().map((cell) => <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>)}</tr>)}</tbody>
  </table></div>
}

export function AdminPage() {
  const [tab, setTab] = useState<Tab>('resumen')
  const [error, setError] = useState('')
  const queryClient = useQueryClient()
  const summary = useQuery({ queryKey: ['admin', 'resumen'], queryFn: async () => (await api.get<Resumen>('/pedidos/resumen')).data })
  const products = useQuery({ queryKey: ['admin', 'productos'], queryFn: async () => (await api.get<Pagina<Producto>>('/productos', { params: { limit: 100 } })).data })
  const categories = useQuery({ queryKey: ['admin', 'categorias'], queryFn: async () => (await api.get<Pagina<Categoria>>('/categorias')).data })
  const orders = useQuery({ queryKey: ['admin', 'pedidos'], queryFn: async () => (await api.get<Pagina<Pedido>>('/pedidos')).data })
  const users = useQuery({ queryKey: ['admin', 'usuarios'], queryFn: async () => (await api.get<Pagina<Usuario>>('/admin/usuarios')).data })
  const refresh = () => queryClient.invalidateQueries({ queryKey: ['admin'] })
  const mutate = useMutation({
    mutationFn: async (action: () => Promise<unknown>) => action(),
    onSuccess: () => { setError(''); refresh() },
    onError: () => setError('La operación no se pudo completar.'),
  })
  const busy = mutate.isPending
  const perform = (action: () => Promise<unknown>) => mutate.mutate(action)

  function createProduct(formData: FormData) {
    perform(() => api.post('/productos', {
      nombre: formData.get('nombre'), descripcion: formData.get('descripcion') || null,
      precio: Number(formData.get('precio')), stock: Number(formData.get('stock')),
      disponible: true, categoria_id: Number(formData.get('categoria_id')),
    }))
  }
  function createCategory(formData: FormData) {
    perform(() => api.post('/categorias', { nombre: formData.get('nombre'), descripcion: formData.get('descripcion') || null }))
  }

  return <section className="admin-page">
    <div className="admin-heading"><div><span className="eyebrow">Administración</span><h1>Panel de control</h1></div></div>
    <div className="admin-tabs" role="tablist">
      {(['resumen', 'productos', 'categorias', 'pedidos', 'usuarios'] as const).map((name) => <button key={name} className={tab === name ? 'selected' : ''} onClick={() => setTab(name)}>{name[0].toUpperCase() + name.slice(1)}</button>)}
    </div>
    {error && <p role="alert" className="admin-error">{error}</p>}

    {tab === 'resumen' && <div className="summary-grid">
      {summary.data && Object.entries({ Total: summary.data.total_pedidos, Pendientes: summary.data.pendientes, 'En preparación': summary.data.en_preparacion, Entregados: summary.data.entregados, Cancelados: summary.data.cancelados }).map(([label, value]) => <article className="summary-card" key={label}><span>{label}</span><strong>{value}</strong></article>)}
      {summary.isLoading && <p>Cargando resumen…</p>}
    </div>}

    {tab === 'productos' && <div className="admin-section">
      <h2>Productos</h2>
      <form action={createProduct} className="admin-form">
        <input name="nombre" placeholder="Nombre" required maxLength={150} />
        <input name="descripcion" placeholder="Descripción" />
        <input name="precio" type="number" min="0.01" step="0.01" placeholder="Precio" required />
        <input name="stock" type="number" min="0" placeholder="Stock" required />
        <select name="categoria_id" required defaultValue=""><option value="" disabled>Categoría</option>{categories.data?.items.map((category) => <option key={category.id} value={category.id}>{category.nombre}</option>)}</select>
        <button disabled={busy}>Crear producto</button>
      </form>
      <ProductTable products={products.data?.items ?? []} busy={busy} perform={perform} />
    </div>}

    {tab === 'categorias' && <div className="admin-section">
      <h2>Categorías</h2>
      <form action={createCategory} className="admin-form"><input name="nombre" placeholder="Nombre de categoría" required maxLength={100} /><input name="descripcion" placeholder="Descripción" /><button disabled={busy}>Crear categoría</button></form>
      <div className="admin-table-wrap"><table><thead><tr><th>Nombre</th><th>Descripción</th><th>Acción</th></tr></thead><tbody>{categories.data?.items.map((category) => <tr key={category.id}><td>{category.nombre}</td><td>{category.descripcion}</td><td><button className="danger" onClick={() => perform(() => api.delete(`/categorias/${category.id}`))} disabled={busy}>Dar de baja</button></td></tr>)}</tbody></table></div>
    </div>}

    {tab === 'pedidos' && <div className="admin-section"><h2>Pedidos</h2><div className="admin-table-wrap"><table><thead><tr><th>N.º</th><th>Fecha</th><th>Cliente ID</th><th>Estado</th><th>Total</th><th>Actualizar estado</th></tr></thead><tbody>
      {orders.data?.items.map((order) => <tr key={order.id}><td>#{order.id}</td><td>{new Date(order.creado_en).toLocaleDateString('es-AR')}</td><td>{order.usuario_id}</td><td>{order.estado.replace('_', ' ')}</td><td>${order.total.toFixed(2)}</td><td><select aria-label={`Cambiar estado del pedido ${order.id}`} value={order.estado} disabled={busy || order.estado === 'ENTREGADO' || order.estado === 'CANCELADO'} onChange={(event) => perform(() => api.patch(`/pedidos/${order.id}/estado`, { estado: event.target.value }))}>
        <option value="PENDIENTE">Pendiente</option><option value="EN_PREPARACION">En preparación</option><option value="ENTREGADO">Entregado</option><option value="CANCELADO">Cancelado</option>
      </select></td></tr>)}
    </tbody></table></div></div>}

    {tab === 'usuarios' && <div className="admin-section"><h2>Usuarios</h2><div className="admin-table-wrap"><table><thead><tr><th>Nombre</th><th>Email</th><th>Rol</th><th>Estado</th><th>Acción</th></tr></thead><tbody>
      {users.data?.items.map((user) => <tr key={user.id}><td>{user.nombre}</td><td>{user.email}</td><td>{user.rol}</td><td>{user.disabled ? 'Desactivado' : 'Activo'}</td><td><button onClick={() => perform(() => api.post(`/admin/usuarios/${user.id}/${user.disabled ? 'activar' : 'desactivar'}`))} disabled={busy}>{user.disabled ? 'Activar' : 'Desactivar'}</button></td></tr>)}
    </tbody></table></div></div>}
  </section>
}
