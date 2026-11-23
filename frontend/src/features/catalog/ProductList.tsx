import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { api } from '../../api/client'
import { useCartStore } from '../../stores/cartStore'
import type { Categoria, Pagina, Producto } from '../../types'

export function ProductList() {
  const [search, setSearch] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const add = useCartStore((state) => state.agregar)
  const categories = useQuery({
    queryKey: ['categorias'],
    queryFn: async () => (await api.get<Pagina<Categoria>>('/categorias')).data.items,
  })
  const products = useQuery({
    queryKey: ['productos', search, categoryId],
    queryFn: async () => (await api.get<Pagina<Producto>>('/productos', {
      params: { search: search || undefined, categoria_id: categoryId || undefined, disponible: true },
    })).data,
  })

  return <section>
    <div className="filters">
      <input aria-label="Buscar productos" placeholder="Buscar comida..." value={search} onChange={(event) => setSearch(event.target.value)} />
      <select aria-label="Filtrar por categoría" value={categoryId} onChange={(event) => setCategoryId(event.target.value)}>
        <option value="">Todas las categorías</option>
        {categories.data?.map((category) => <option key={category.id} value={category.id}>{category.nombre}</option>)}
      </select>
    </div>
    {products.isLoading && <p>Cargando catálogo…</p>}
    {products.isError && <p role="alert">No se pudo cargar el catálogo.</p>}
    <div className="product-grid">
      {products.data?.items.map((product) => <article className="card" key={product.id}>
        <span className="eyebrow">{categories.data?.find((category) => category.id === product.categoria_id)?.nombre ?? 'Food Store'}</span>
        <h2>{product.nombre}</h2>
        <p>{product.descripcion}</p>
        <div className="card-bottom"><strong>${product.precio.toFixed(2)}</strong><button disabled={!product.disponible || product.stock < 1} onClick={() => add({ producto_id: product.id, nombre: product.nombre, precio: product.precio })}>Agregar</button></div>
      </article>)}
    </div>
  </section>
}
