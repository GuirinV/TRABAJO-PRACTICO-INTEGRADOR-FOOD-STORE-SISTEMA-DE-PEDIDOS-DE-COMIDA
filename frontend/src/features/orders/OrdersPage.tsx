import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../../api/client'
import type { Pagina, Pedido } from '../../types'

export function OrdersPage() {
  const queryClient = useQueryClient()
  const orders = useQuery({ queryKey: ['pedidos'], queryFn: async () => (await api.get<Pagina<Pedido>>('/pedidos')).data })
  const cancel = useMutation({
    mutationFn: async (id: number) => (await api.post<Pedido>(`/pedidos/${id}/cancelar`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['pedidos'] }),
  })

  return <section className="narrow">
    <h1>Mis pedidos</h1>
    {orders.isLoading && <p>Cargando pedidos…</p>}
    {orders.isError && <p role="alert">No se pudieron cargar los pedidos.</p>}
    {orders.data?.items.length === 0 && <p>Todavía no tenés pedidos.</p>}
    <div className="order-list">{orders.data?.items.map((order) => <article className="card order-card" key={order.id}>
      <div className="order-heading"><div><span className="eyebrow">Pedido #{order.id}</span><h2>{order.estado.replace('_', ' ')}</h2></div><strong>${order.total.toFixed(2)}</strong></div>
      <p>{new Date(order.creado_en).toLocaleString('es-AR')} · {order.forma_pago}</p>
      <p>{order.direccion_entrega}</p>
      <ul>{order.items.map((item) => <li key={item.id}>{item.cantidad} × {item.nombre_producto} — ${item.subtotal.toFixed(2)}</li>)}</ul>
      {order.estado === 'PENDIENTE' && <button className="secondary" onClick={() => cancel.mutate(order.id)} disabled={cancel.isPending}>Cancelar pedido</button>}
    </article>)}</div>
  </section>
}
