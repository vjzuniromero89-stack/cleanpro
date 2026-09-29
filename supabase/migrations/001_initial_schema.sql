-- CleanPro initial schema. Run after creating a Supabase project.
create extension if not exists pgcrypto;
create table if not exists public.profiles(id uuid primary key references auth.users(id) on delete cascade,full_name text,phone text,role text not null default 'customer' check(role in ('customer','admin','super_admin')),created_at timestamptz not null default now(),updated_at timestamptz not null default now());
create table if not exists public.service_catalog(id text primary key,name text not null,category text not null,unit text not null check(unit in ('flat','sqft','each','room','bath')),price numeric(10,3) not null default 0,description text,property_types text[] not null default '{all}',active boolean not null default true,sort_order int default 0,created_at timestamptz not null default now());
create table if not exists public.pricing_settings(id int primary key default 1 check(id=1),minimum_visit numeric(10,2) not null default 85,weekly_discount numeric(5,4) default .15,twice_weekly_discount numeric(5,4) default .20,biweekly_discount numeric(5,4) default .10,monthly_discount numeric(5,4) default .05,deep_multiplier numeric(5,2) default 1.25,heavy_multiplier numeric(5,2) default 1.50,updated_at timestamptz default now());
insert into public.pricing_settings(id) values(1) on conflict do nothing;
create table if not exists public.quotes(id uuid primary key default gen_random_uuid(),user_id uuid not null references auth.users(id) on delete cascade,property_type text not null,square_feet int not null default 0,bedrooms numeric default 0,bathrooms numeric default 0,floors int default 1,condition text default 'standard',frequency text default 'once',subtotal numeric(10,2) not null default 0,discount numeric(10,2) not null default 0,total numeric(10,2) not null default 0,status text not null default 'draft' check(status in ('draft','saved','accepted','expired','cancelled')),contact jsonb default '{}'::jsonb,created_at timestamptz not null default now(),updated_at timestamptz not null default now());
create table if not exists public.quote_items(id bigint generated always as identity primary key,quote_id uuid not null references public.quotes(id) on delete cascade,service_id text references public.service_catalog(id),service_name text not null,quantity numeric not null default 1,unit_price numeric(10,3) not null,total numeric(10,2) not null,created_at timestamptz default now());
create table if not exists public.bookings(id uuid primary key default gen_random_uuid(),user_id uuid not null references auth.users(id) on delete cascade,quote_id uuid references public.quotes(id) on delete set null,scheduled_at timestamptz,address text,notes text,status text not null default 'pending' check(status in ('pending','confirmed','in_progress','completed','cancelled')),payment_status text not null default 'unpaid' check(payment_status in ('unpaid','pending','paid','refunded','partial')),stripe_checkout_session_id text,stripe_payment_intent_id text,created_at timestamptz default now(),updated_at timestamptz default now());
create table if not exists public.payments(id uuid primary key default gen_random_uuid(),user_id uuid not null references auth.users(id) on delete cascade,booking_id uuid references public.bookings(id) on delete set null,amount numeric(10,2) not null,currency text default 'usd',status text not null,stripe_payment_intent_id text unique,created_at timestamptz default now());

alter table public.profiles enable row level security;alter table public.service_catalog enable row level security;alter table public.pricing_settings enable row level security;alter table public.quotes enable row level security;alter table public.quote_items enable row level security;alter table public.bookings enable row level security;alter table public.payments enable row level security;

create or replace function public.is_admin() returns boolean language sql stable security invoker set search_path='' as $$ select coalesce((auth.jwt()->'app_metadata'->>'role') in ('admin','super_admin'),false) $$;
revoke all on function public.is_admin() from public; grant execute on function public.is_admin() to authenticated;

create policy "profile read own or admin" on public.profiles for select to authenticated using ((select auth.uid())=id or (select public.is_admin()));
create policy "profile update own" on public.profiles for update to authenticated using ((select auth.uid())=id) with check ((select auth.uid())=id);
create policy "catalog public read" on public.service_catalog for select to anon,authenticated using(active=true or (select public.is_admin()));
create policy "catalog admin write" on public.service_catalog for all to authenticated using((select public.is_admin())) with check((select public.is_admin()));
create policy "settings public read" on public.pricing_settings for select to anon,authenticated using(true);
create policy "settings admin write" on public.pricing_settings for all to authenticated using((select public.is_admin())) with check((select public.is_admin()));
create policy "quotes own or admin read" on public.quotes for select to authenticated using((select auth.uid())=user_id or (select public.is_admin()));
create policy "quotes own insert" on public.quotes for insert to authenticated with check((select auth.uid())=user_id);
create policy "quotes own update" on public.quotes for update to authenticated using((select auth.uid())=user_id or (select public.is_admin())) with check((select auth.uid())=user_id or (select public.is_admin()));
create policy "quotes own delete" on public.quotes for delete to authenticated using((select auth.uid())=user_id or (select public.is_admin()));
create policy "items read via quote" on public.quote_items for select to authenticated using(exists(select 1 from public.quotes q where q.id=quote_id and (q.user_id=(select auth.uid()) or (select public.is_admin()))));
create policy "items insert via quote" on public.quote_items for insert to authenticated with check(exists(select 1 from public.quotes q where q.id=quote_id and q.user_id=(select auth.uid())));
create policy "items delete via quote" on public.quote_items for delete to authenticated using(exists(select 1 from public.quotes q where q.id=quote_id and (q.user_id=(select auth.uid()) or (select public.is_admin()))));
create policy "bookings own or admin read" on public.bookings for select to authenticated using((select auth.uid())=user_id or (select public.is_admin()));
create policy "bookings own insert" on public.bookings for insert to authenticated with check((select auth.uid())=user_id);
create policy "bookings own/admin update" on public.bookings for update to authenticated using((select auth.uid())=user_id or (select public.is_admin())) with check((select auth.uid())=user_id or (select public.is_admin()));
create policy "payments own/admin read" on public.payments for select to authenticated using((select auth.uid())=user_id or (select public.is_admin()));

insert into public.service_catalog(id,name,category,unit,price,description,property_types,sort_order) values
('bathroom','Baños completos','Áreas','bath',25,'Inodoro, lavamanos, espejo, superficies, piso y basura','{all}',10),
('kitchen','Cocina','Áreas','flat',35,'Counters, fregadero y superficies','{single,townhouse,apartment}',20),
('bedroom','Dormitorios','Áreas','room',15,'Polvo, superficies y piso','{single,townhouse,apartment}',30),
('living','Sala / Living Room','Áreas','flat',20,'Polvo, superficies y piso','{single,townhouse,apartment}',40),
('sweepmop','Barrer y mapear pisos','Pisos','sqft',.045,'Piso duro barrido y trapeado','{all}',50),
('vacuum','Aspirar alfombra','Pisos','sqft',.04,'Aspirado de alfombra','{all}',60),
('desks','Escritorios / estaciones','Comercial','each',4,'Superficie y desinfección ligera','{office,bank,clinic}',70),
('trash','Vaciar botes de basura','Comercial','each',2.5,'Retiro y reemplazo de bolsa','{office,retail,restaurant,bank,clinic,warehouse}',80),
('fridge','Interior refrigerador','Extras','flat',45,'Refrigerador vacío','{single,townhouse,apartment}',90),
('oven','Interior horno','Extras','flat',40,'Limpieza interior estándar','{single,townhouse,apartment}',100),
('baseboards','Zócalos / Baseboards','Extras','flat',40,'Limpieza detallada','{all}',110)
on conflict(id) do update set name=excluded.name,category=excluded.category,unit=excluded.unit,price=excluded.price,description=excluded.description,property_types=excluded.property_types,sort_order=excluded.sort_order;

-- Optional profile creation trigger.
create or replace function public.handle_new_user() returns trigger language plpgsql security definer set search_path='' as $$ begin insert into public.profiles(id,full_name) values(new.id,coalesce(new.raw_user_meta_data->>'full_name','')) on conflict do nothing; return new; end; $$;
revoke all on function public.handle_new_user() from public,anon,authenticated;
drop trigger if exists on_auth_user_created on auth.users;create trigger on_auth_user_created after insert on auth.users for each row execute function public.handle_new_user();
