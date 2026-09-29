# CleanPro

Aplicación completa base para cotización y reserva de limpieza residencial/comercial. Diseñada para subirse a GitHub y desplegarse en Vercel, conectando después Supabase y Stripe.

## Incluido
- Frontpage responsive.
- Cotizador dinámico por propiedad, ft², habitaciones, baños, condición, tareas, cantidades y frecuencia.
- Servicios residenciales y comerciales; el cliente puede agregar y eliminar tareas.
- Total en tiempo real, mínimo por visita y descuentos por frecuencia.
- Portal de cuenta y autenticación preparados para Supabase Auth.
- Panel administrativo y catálogo maestro.
- Migración SQL con perfiles, catálogo, pricing, quotes, items, bookings y payments + RLS.
- Stripe Checkout preparado; no usa claves hasta que tú las agregues.
- Modo local/demo cuando Supabase todavía no está conectado.

## Ejecutar local
1. Instala Node 22 LTS.
2. `npm install`
3. Copia `.env.example` a `.env.local` (puede quedar vacío para probar el cotizador).
4. `npm run dev`

## Conectar Supabase después
1. Crea un proyecto Supabase.
2. Ejecuta `supabase/migrations/001_initial_schema.sql` en SQL Editor.
3. Copia URL y publishable key a `.env.local` / variables de Vercel.
4. Para dar rol admin, usa `app_metadata.role` = `admin` o `super_admin`; no uses `user_metadata` para autorización.

## Conectar Stripe después
Agrega `STRIPE_SECRET_KEY`, `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` y luego configura el webhook para confirmar pagos y crear/actualizar reservas. El botón Checkout ya está preparado para crear una sesión cuando exista la clave secreta.

## Nota de precios
Los precios incluidos son valores iniciales de configuración y deben ajustarse a costos reales, alcance, mercado, materiales, salarios y margen del negocio. Trabajos especiales pueden requerir inspección.
