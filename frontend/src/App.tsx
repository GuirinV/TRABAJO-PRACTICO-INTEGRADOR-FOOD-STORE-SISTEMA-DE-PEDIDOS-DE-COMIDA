import { useEffect } from 'react'
import { Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { api } from './api/client'
import { CartPage } from './features/cart/CartPage'
import { AdminPage } from './features/admin/AdminPage'
import { useAuthStore } from './features/auth/authStore'
import { useForm } from '@tanstack/react-form'
import { ProductList } from './features/catalog/ProductList'
import { OrdersPage } from './features/orders/OrdersPage'
import type { Usuario } from './types'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((state) => state.user)
  return user ? children : <Navigate to="/" replace />
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((state) => state.user)
  return user?.rol === 'admin' ? children : <Navigate to="/" replace />
}

function LoginForm() {
  const setUser = useAuthStore((state) => state.setUser)
  const navigate = useNavigate()
  const mutation = useMutation({
    mutationFn: async (values: { email: string; password: string }) => {
      await api.post('/auth/token', new URLSearchParams({ username: values.email, password: values.password }), { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
      return (await api.get<Usuario>('/auth/me')).data
    },
    onSuccess: (user) => { setUser(user); navigate('/') },
  })
  const form = useForm({
    defaultValues: { email: '', password: '' },
    onSubmit: async ({ value }) => mutation.mutateAsync(value),
  })
  return <form className="login-form" onSubmit={(event) => { event.preventDefault(); event.stopPropagation(); void form.handleSubmit() }}>
    <form.Field name="email" validators={{ onChange: ({ value }) => !value.includes('@') ? 'Ingresá un email válido.' : undefined }}>
      {(field) => <label>Email<input type="email" value={field.state.value} onChange={(event) => field.handleChange(event.target.value)} required /></label>}
    </form.Field>
    <form.Field name="password" validators={{ onChange: ({ value }) => value.length < 8 ? 'La contraseña debe tener al menos 8 caracteres.' : undefined }}>
      {(field) => <label>Contraseña<input type="password" value={field.state.value} onChange={(event) => field.handleChange(event.target.value)} required /></label>}
    </form.Field>
    {mutation.isError && <p role="alert">No se pudo iniciar sesión.</p>}
    <button disabled={mutation.isPending}>Ingresar</button>
  </form>
}

function RegisterForm() {
  const navigate = useNavigate()
  const mutation = useMutation({
    mutationFn: async (values: { nombre: string; email: string; password: string }) => api.post<Usuario>('/auth/register', {
      nombre: values.nombre, email: values.email, password: values.password,
    }),
    onSuccess: () => navigate('/ingresar'),
  })
  const form = useForm({
    defaultValues: { nombre: '', email: '', password: '' },
    onSubmit: async ({ value }) => mutation.mutateAsync(value),
  })
  return <form className="login-form" onSubmit={(event) => { event.preventDefault(); event.stopPropagation(); void form.handleSubmit() }}>
    <form.Field name="nombre" validators={{ onChange: ({ value }) => value.trim() ? undefined : 'Ingresá tu nombre.' }}>
      {(field) => <label>Nombre<input value={field.state.value} onChange={(event) => field.handleChange(event.target.value)} required maxLength={100} /></label>}
    </form.Field>
    <form.Field name="email" validators={{ onChange: ({ value }) => !value.includes('@') ? 'Ingresá un email válido.' : undefined }}>
      {(field) => <label>Email<input type="email" value={field.state.value} onChange={(event) => field.handleChange(event.target.value)} required /></label>}
    </form.Field>
    <form.Field name="password" validators={{ onChange: ({ value }) => value.length < 8 ? 'La contraseña debe tener al menos 8 caracteres.' : undefined }}>
      {(field) => <label>Contraseña<input type="password" value={field.state.value} onChange={(event) => field.handleChange(event.target.value)} required minLength={8} /></label>}
    </form.Field>
    {mutation.isError && <p role="alert">No se pudo crear la cuenta.</p>}
    <button disabled={mutation.isPending}>Crear cuenta</button>
  </form>
}

function App() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const setUser = useAuthStore((state) => state.setUser)
  const setInitialized = useAuthStore((state) => state.setInitialized)
  const session = useQuery({
    queryKey: ['sesion'],
    queryFn: async () => (await api.get<Usuario>('/auth/me')).data,
    retry: false,
  })
  const logout = useMutation({ mutationFn: () => api.post('/auth/logout'), onSuccess: () => { setUser(null); navigate('/') } })

  useEffect(() => {
    if (session.data) setUser(session.data)
    if (session.isFetched) setInitialized(true)
  }, [session.data, session.isFetched, setInitialized, setUser])
  useEffect(() => {
    const unauthorized = () => setUser(null)
    window.addEventListener('foodstore:unauthorized', unauthorized)
    return () => window.removeEventListener('foodstore:unauthorized', unauthorized)
  }, [setUser])

  return <div className="app-shell">
    <header className="site-header"><Link className="brand" to="/">Food Store<span>.</span></Link><nav>
      <Link to="/">Menú</Link>
      {user && <><Link to="/mis-pedidos">Mis pedidos</Link><Link to="/carrito">Carrito</Link><button className="nav-button" onClick={() => logout.mutate()}>Salir</button></>}
      {user?.rol === 'admin' && <Link to="/admin">Admin</Link>}
      {!user && <><Link to="/ingresar">Ingresar</Link><Link to="/registro">Crear cuenta</Link></>}
    </nav></header>
    <main><Routes>
      <Route path="/" element={<><section className="hero"><span className="eyebrow">Hecho para disfrutar</span><h1>Tu próximo favorito<br />está a un pedido.</h1><p>Elegí, pedí y disfrutá. Simple y rico.</p></section><ProductList /></>} />
      <Route path="/ingresar" element={<section className="narrow"><h1>Ingresar</h1><LoginForm /></section>} />
      <Route path="/registro" element={<section className="narrow"><h1>Crear cuenta</h1><RegisterForm /></section>} />
      <Route path="/carrito" element={<ProtectedRoute><CartPage /></ProtectedRoute>} />
      <Route path="/mis-pedidos" element={<ProtectedRoute><OrdersPage /></ProtectedRoute>} />
      <Route path="/admin" element={<AdminRoute><AdminPage /></AdminRoute>} />
    </Routes></main>
    <footer>Food Store · Comida rica, sin vueltas.</footer>
  </div>
}

export default App
