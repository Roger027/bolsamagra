create table if not exists public.finance_state (
    id text primary key check (id = 'shared'),
    payload jsonb not null default '{}'::jsonb,
    version bigint not null default 0,
    updated_at timestamptz not null default now()
);

insert into public.finance_state (id, payload, version)
values ('shared', '{}'::jsonb, 0)
on conflict (id) do nothing;

alter table public.finance_state enable row level security;

revoke all on table public.finance_state from anon, authenticated;
grant all on table public.finance_state to service_role;

create or replace function public.save_finance_state(
    p_expected_version bigint,
    p_payload jsonb
)
returns bigint
language plpgsql
security definer
set search_path = ''
as $$
declare
    nova_versao bigint;
begin
    update public.finance_state
       set payload = p_payload,
           version = version + 1,
           updated_at = now()
     where id = 'shared'
       and version = p_expected_version
    returning version into nova_versao;

    if nova_versao is null then
        raise exception 'Finance data changed; reload before saving'
            using errcode = '40001';
    end if;

    return nova_versao;
end;
$$;

revoke all on function public.save_finance_state(bigint, jsonb)
    from public, anon, authenticated;
grant execute on function public.save_finance_state(bigint, jsonb)
    to service_role;
