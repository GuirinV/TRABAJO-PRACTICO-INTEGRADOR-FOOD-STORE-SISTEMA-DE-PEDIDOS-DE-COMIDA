import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { api } from '../../api/client'
import { useCartStore } from '../../stores/cartStore'
import type { Pedido } from '../../types'

export function CartPage() {
  const navigate = useNavigate()
  const items = useCartStore((state) => state.items)
  const setQuantity = useCartStore((state) => state.cambiarCantidad)
  const remove = useCartStore((state) => state.quitar)
  const clear = useCartStore((state) => state.limpiar)
  const total = items.reduce((sum, item) => sum + item.precio * item.cantidad, 0)
  const mutation = useMutation({
    mutationFn: async (values: { direccion_entrega: string; forma_pago: 'EFECTIVO' | 'TRANSFERENCIA' }) => {
      const response = await api.post<Pedido>('/pedidos', {
        ...values,
        items: items.map(({ producto_id, cantidad }) => ({ producto_id, cantidad })),
      })
      return response.data
    },
    onSuccess: () => { clear(); navigate('/mis-pedidos') },
  })

  function checkout(formData: FormData) {
    mutation.mutate({
      direccion_entrega: String(formData.get('direccion_entrega') ?? ''),
      forma_pago: String(formData.get('forma_pago') ?? 'EFECTIVO') as 'EFECTIVO' | 'TRANSFERENCIA',
    })
  }

  return <section className="narrow">
    <h1>Tu carrito</h1>
    {items.length === 0 ? <p>El carrito está vacío. <a href="/">Volver al catálogo</a></p> : <>
      <div className="cart-lines">{items.map((item) => <article className="cart-line" key={item.producto_id}>
        <div><strong>{item.nombre}</strong><p>${item.precio.toFixed(2)} c/u</p></div>
        <input aria-label={`Cantidad de ${item.nombre}`} type="number" min="1" value={item.cantidad} onChange={(event) => setQuantity(item.producto_id, Number(event.target.value))} />
        <button className="text-button" onClick={() => remove(item.producto_id)}>Quitar</button>
      </article>)}</div>
      <p className="total">Total estimado: ${total.toFixed(2)}</p>
      <form action={checkout} className="checkout-form">
        <label>Dirección de entrega<input name="direccion_entrega" minLength={5} maxLength={200} required /></label>
        <label>Forma de pago<select name="forma_pago"><option value="EFECTIVO">Efectivo</option><option value="TRANSFERENCIA">Transferencia</option></select></label>
        {mutation.isError && <p role="alert">No se pudo crear el pedido. Revisá sesión y disponibilidad del stock.</p>}
        <button disabled={mutation.isPending}>{mutation.isPending ? 'Enviando…' : 'Confirmar pedido'}</button>
      </form>
    </>}
  </section>
}
