-- Supabase/Postgres schema for Telegram Clothing Order Bot.
-- Supabase is the source of truth. Google Sheets/Excel are export targets only.

create table if not exists orders (
    id bigserial primary key,
    order_code text unique,
    order_date date not null,
    customer_name text not null,
    phone text not null,
    item text not null,
    size text,
    color text,
    quantity integer not null default 1 check (quantity > 0),
    amount integer not null default 0 check (amount >= 0),
    payment_status text not null check (payment_status in ('Paid', 'Unpaid', 'COD', 'Deposit')),
    payment_method text,
    delivery_status text not null check (delivery_status in ('Pending', 'Delivered', 'Pickup', 'Cancelled', 'Returned')),
    address_note text,
    status text not null default 'Open' check (status in ('Open', 'Closed', 'Cancelled')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create or replace function set_order_code()
returns trigger
language plpgsql
as $$
begin
    if new.order_code is null or new.order_code = '' then
        new.order_code := 'C-' || lpad(new.id::text, 4, '0');
    end if;
    return new;
end;
$$;

drop trigger if exists trg_set_order_code on orders;
create trigger trg_set_order_code
before insert on orders
for each row
execute function set_order_code();

create or replace function set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at := now();
    return new;
end;
$$;

drop trigger if exists trg_orders_updated_at on orders;
create trigger trg_orders_updated_at
before update on orders
for each row
execute function set_updated_at();

create index if not exists idx_orders_order_date on orders(order_date);
create index if not exists idx_orders_unpaid on orders(status, payment_status);
create index if not exists idx_orders_delivery on orders(status, delivery_status);
create index if not exists idx_orders_phone on orders(phone);

create table if not exists user_settings (
    telegram_user_id bigint primary key,
    username text,
    first_name text,
    language text not null check (language in ('en', 'my')),
    role text not null default 'seller' check (role in ('seller', 'admin')),
    updated_at timestamptz not null default now()
);

drop trigger if exists trg_user_settings_updated_at on user_settings;
create trigger trg_user_settings_updated_at
before update on user_settings
for each row
execute function set_updated_at();
