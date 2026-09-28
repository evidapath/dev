-- =========================================================================
-- EvidaPath student profile + saved universities (Discover/Analyze persistence)
-- Applied to production 2026-09-27 via Supabase migration
-- `student_profile_and_saved_universities`.
--
-- Mirrors the Offer Vault security model:
--   - RLS enabled; a student may only touch their own rows (user_id = auth.uid())
--   - references Sanity by text id (sanity_university_id); never duplicates
--     public university facts
--   - reuses the existing hardened public.set_updated_at() trigger function
-- =========================================================================

-- 1. student_profiles: the shared profile, filled once (one row per user)
create table if not exists public.student_profiles (
  id                uuid primary key default gen_random_uuid(),
  user_id           uuid not null unique references auth.users(id) on delete cascade,
  curriculum        text,
  grade_band        text,
  intended_subject  text,
  academic_level    text check (academic_level is null or academic_level in ('undergraduate','postgraduate')),
  preferred_region  text,
  annual_budget     numeric check (annual_budget is null or annual_budget >= 0),
  budget_currency   text not null default 'USD' check (budget_currency ~ '^[A-Z]{3}$'),
  citizenship       text,
  preferences       text,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);
create index if not exists idx_student_profiles_user on public.student_profiles(user_id);

-- 2. student_saved_universities: the student's "My Path" university picks
create table if not exists public.student_saved_universities (
  id                   uuid primary key default gen_random_uuid(),
  user_id              uuid not null references auth.users(id) on delete cascade,
  sanity_university_id text not null,
  university_name      text,
  note                 text,
  saved_at             timestamptz not null default now(),
  unique (user_id, sanity_university_id)
);
create index if not exists idx_student_saved_universities_user on public.student_saved_universities(user_id);

-- updated_at trigger (reuse existing hardened function)
drop trigger if exists trg_student_profiles_updated on public.student_profiles;
create trigger trg_student_profiles_updated before update on public.student_profiles
  for each row execute function public.set_updated_at();

-- RLS
alter table public.student_profiles enable row level security;
alter table public.student_saved_universities enable row level security;

drop policy if exists "student_profiles_all_own" on public.student_profiles;
create policy "student_profiles_all_own" on public.student_profiles
  for all to authenticated
  using (auth.uid() is not null and user_id = auth.uid())
  with check (auth.uid() is not null and user_id = auth.uid());

drop policy if exists "student_saved_universities_all_own" on public.student_saved_universities;
create policy "student_saved_universities_all_own" on public.student_saved_universities
  for all to authenticated
  using (auth.uid() is not null and user_id = auth.uid())
  with check (auth.uid() is not null and user_id = auth.uid());
