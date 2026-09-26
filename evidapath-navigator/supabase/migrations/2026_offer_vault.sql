-- =========================================================================
-- EvidaPath Offer Vault — Private student workflow schema (FINAL REVISED)
-- Run in: Supabase → SQL Editor → New query → paste & run
--
-- DO NOT RUN automatically. Return for review/approval first.
--
-- System boundaries:
--   Sanity   = PUBLIC education-market intelligence (universities, costs, scholarships)
--   Supabase = PRIVATE student data (applications, offers, awards, documents,
--              enrollment decisions, outcomes)
--
-- This migration creates ONLY private student tables. Public scholarship /
-- university data is referenced by Sanity record IDs (text), never duplicated.
--
-- Execution order (this revision):
--   1. extensions / helper primitives
--   2. tables + indexes (NO triggers yet)
--   3. trigger functions
--   4. triggers
--   5. RLS policies
--   6. storage bucket + policies
--
-- Security hardening:
--   1. Same-owner parent/child integrity enforced at the DB level via composite
--      foreign keys (+ scoped triggers for optional links: awards.document_id
--      and outcomes.enrollment_decision_id).
--   2. verification_level promotion is locked: ordinary authenticated users can
--      never set anything but 'self_reported'; only a trusted service-role /
--      admin backend may upgrade to document_verified / institution_verified.
--      Edits to MATERIAL fields on a verified record auto-reset to
--      self_reported (no stale verified claims).
--   3. Supabase Storage hardened: owner_id compared as TEXT, authenticated only,
--      user-scoped path <auth-user-id>/<offer-id>/<file>, foldername()[1]
--      enforced, full path validated at the DB level.
--   4. RLS enabled on all six tables; policies scoped TO authenticated with
--      auth.uid() ownership checks. No service-role key for student CRUD.
--   5. Basic data-integrity constraints (non-negative money, positive duration,
--      non-negative file size, normalized 3-letter uppercase currency).
--
-- All tables are RLS-enabled. A student may only SELECT/INSERT/UPDATE/DELETE
-- their own rows (user_id = auth.uid()). Do NOT disable RLS.
-- =========================================================================

-- =========================================================================
-- 1. EXTENSIONS + HELPER PRIMITIVES
-- =========================================================================

create extension if not exists "pgcrypto";

-- Reusable updated_at trigger
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ---------------------------------------------------------------------------
-- Trusted-role detector.
-- Returns true ONLY when the current database session is running as a
-- privileged EvidaPath backend role (service_role / postgres / supabase_admin
-- / admin). Ordinary anon/authenticated users return false.
--
-- Supabase maps the service-role JWT to the `service_role` database role,
-- which BYPASSRLS. The anon key maps to `anon`; the authenticated user's
-- session maps to `authenticated`. This function is the single gate used by
-- the verification-level triggers.
-- ---------------------------------------------------------------------------
create or replace function public.is_evidapath_trusted_role()
returns boolean language sql stable as $$
  select coalesce(current_setting('role', true), '') in
    ('service_role', 'postgres', 'supabase_admin', 'admin');
$$;

-- =========================================================================
-- 2. TABLES + INDEXES  (no triggers yet — functions come in section 3)
-- =========================================================================

-- -------------------------------------------------------------------------
-- 2a. student_applications
-- -------------------------------------------------------------------------
create table if not exists public.student_applications (
  id                  uuid primary key default gen_random_uuid(),
  user_id             uuid not null references auth.users(id) on delete cascade,
  sanity_university_id text not null,
  sanity_program_id   text,
  sanity_campus_id    text,
  university_name     text not null,
  program_name        text,
  application_cycle   text,
  decision_plan       text,
  application_date    date,
  status              text not null default 'planning'
    check (status in ('planning','started','submitted','in_review','waitlisted','admitted','rejected','withdrawn')),
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now()
);

-- Unique composite key so child tables can reference (user_id, id) and the
-- database can guarantee the child's user_id matches the parent's user_id.
create unique index if not exists uq_student_applications_user_id_id
  on public.student_applications(user_id, id);

create index if not exists idx_student_applications_user on public.student_applications(user_id);

-- -------------------------------------------------------------------------
-- 2b. student_offers  (created when an application is admitted)
--     Composite FK (user_id, application_id) -> student_applications(user_id, id)
--     guarantees the offer cannot attach to another user's application.
-- -------------------------------------------------------------------------
create table if not exists public.student_offers (
  id                       uuid primary key default gen_random_uuid(),
  user_id                  uuid not null references auth.users(id) on delete cascade,
  application_id           uuid not null,
  admission_result         text not null default 'admitted',
  official_offer_date      date,
  response_deadline        date,
  enrollment_deposit_amount numeric
    check (enrollment_deposit_amount is null or enrollment_deposit_amount >= 0),
  deposit_deadline         date,
  currency                 text not null default 'USD'
    check (currency ~ '^[A-Z]{3}$'),
  conditions_of_admission  text,
  notes                    text,
  verification_level       text not null default 'self_reported'
    check (verification_level in ('self_reported','document_verified','institution_verified')),
  created_at               timestamptz not null default now(),
  updated_at               timestamptz not null default now(),
  -- composite FK: offer.user_id MUST equal the referenced application.user_id
  constraint fk_student_offers_application_owner
    foreign key (user_id, application_id)
    references public.student_applications(user_id, id)
    on delete cascade
);

create unique index if not exists uq_student_offers_user_id_id
  on public.student_offers(user_id, id);

create index if not exists idx_student_offers_user on public.student_offers(user_id);
create index if not exists idx_student_offers_application on public.student_offers(application_id);

-- -------------------------------------------------------------------------
-- 2c. student_offer_documents  (metadata; files live in Supabase Storage)
--     Created BEFORE student_awards because awards.document_id references it.
--     Composite FK (user_id, offer_id) -> student_offers(user_id, id).
--     storage_path MUST be <user-id>/<offer-id>/<file> (trigger, section 4).
-- -------------------------------------------------------------------------
create table if not exists public.student_offer_documents (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references auth.users(id) on delete cascade,
  offer_id       uuid not null,
  document_type  text not null
    check (document_type in ('offer_letter','scholarship_letter','financial_aid_letter','award_notice','enrollment_confirmation','other')),
  storage_path   text not null,   -- path in the private student-documents bucket
  file_name      text not null,
  mime_type      text,
  size_bytes     bigint
    check (size_bytes is null or size_bytes >= 0),
  uploaded_at    timestamptz not null default now(),
  -- composite FK: document.user_id MUST equal the referenced offer.user_id
  constraint fk_student_offer_documents_offer_owner
    foreign key (user_id, offer_id)
    references public.student_offers(user_id, id)
    on delete cascade
);

create index if not exists idx_student_offer_documents_user on public.student_offer_documents(user_id);
create index if not exists idx_student_offer_documents_offer on public.student_offer_documents(offer_id);

-- -------------------------------------------------------------------------
-- 2d. student_awards  (multiple awards per offer)
--     Composite FK (user_id, offer_id) -> student_offers(user_id, id).
--     Optional document_id ownership enforced by trigger (composite FK is
--     awkward for an optional link, so a scoped trigger guards it instead).
-- -------------------------------------------------------------------------
create table if not exists public.student_awards (
  id                    uuid primary key default gen_random_uuid(),
  user_id               uuid not null references auth.users(id) on delete cascade,
  offer_id              uuid not null,
  sanity_scholarship_id text,  -- reference to public scholarship record (optional)
  award_name            text not null,
  award_type            text not null
    check (award_type in ('scholarship','grant','need_based_aid','merit_aid','tuition_waiver','housing_award','government_sponsorship','external_scholarship','other')),
  amount                numeric
    check (amount is null or amount >= 0),
  currency              text not null default 'USD'
    check (currency ~ '^[A-Z]{3}$'),
  frequency             text not null default 'annual_renewable'
    check (frequency in ('one_time','annual_renewable','per_term','other')),
  duration_years        numeric
    check (duration_years is null or duration_years > 0),
  renewal_criteria      text,
  min_gpa               numeric
    check (min_gpa is null or min_gpa >= 0),
  need_vs_merit         text check (need_vs_merit in ('need_based','merit_based','hybrid','unspecified')),
  document_id           uuid,  -- references student_offer_documents(id); ownership checked by trigger
  verification_level    text not null default 'self_reported'
    check (verification_level in ('self_reported','document_verified','institution_verified')),
  created_at            timestamptz not null default now(),
  updated_at            timestamptz not null default now(),
  -- composite FK: award.user_id MUST equal the referenced offer.user_id
  constraint fk_student_awards_offer_owner
    foreign key (user_id, offer_id)
    references public.student_offers(user_id, id)
    on delete cascade,
  -- simple FK for cascade behavior on the optional document link
  constraint fk_student_awards_document
    foreign key (document_id)
    references public.student_offer_documents(id)
    on delete set null
);

create index if not exists idx_student_awards_user on public.student_awards(user_id);
create index if not exists idx_student_awards_offer on public.student_awards(offer_id);

-- -------------------------------------------------------------------------
-- 2e. student_enrollment_decisions
--     Composite FK (user_id, offer_id) -> student_offers(user_id, id).
-- -------------------------------------------------------------------------
create table if not exists public.student_enrollment_decisions (
  id                                   uuid primary key default gen_random_uuid(),
  user_id                              uuid not null references auth.users(id) on delete cascade,
  offer_id                             uuid not null,
  decision                             text not null
    check (decision in ('accepted','declined','deferred','waitlist_accepted','withdrawn')),
  enrollment_term                      text,
  final_award_accepted                 numeric
    check (final_award_accepted is null or final_award_accepted >= 0),
  expected_first_year_family_contribution numeric
    check (expected_first_year_family_contribution is null or expected_first_year_family_contribution >= 0),
  recorded_at                          timestamptz not null default now(),
  constraint fk_student_enrollment_decisions_offer_owner
    foreign key (user_id, offer_id)
    references public.student_offers(user_id, id)
    on delete cascade
);

create unique index if not exists uq_student_enrollment_decisions_user_id_id
  on public.student_enrollment_decisions(user_id, id);

create index if not exists idx_student_enrollment_decisions_user on public.student_enrollment_decisions(user_id);
create index if not exists idx_student_enrollment_decisions_offer on public.student_enrollment_decisions(offer_id);

-- -------------------------------------------------------------------------
-- 2f. student_outcomes  (longitudinal; designed for future extension)
--     SAFE optional link: enrollment_decision_id is nullable with a simple
--     FK ON DELETE SET NULL (no composite SET NULL on a NOT NULL user_id).
--     Same-user ownership of the optional link is enforced by a trigger
--     (section 4), analogous to the awards.document_id guard.
-- -------------------------------------------------------------------------
create table if not exists public.student_outcomes (
  id                                   uuid primary key default gen_random_uuid(),
  user_id                              uuid not null references auth.users(id) on delete cascade,
  enrollment_decision_id               uuid,
  actual_first_year_cost               numeric
    check (actual_first_year_cost is null or actual_first_year_cost >= 0),
  scholarship_renewed                  boolean,
  transferred                          boolean,
  major_change                         boolean,
  graduated                            boolean,
  employment_or_further_study          text,
  recorded_at                          timestamptz not null default now(),
  -- simple FK: safe SET NULL because enrollment_decision_id is nullable
  constraint fk_student_outcomes_enrollment
    foreign key (enrollment_decision_id)
    references public.student_enrollment_decisions(id)
    on delete set null
);

create index if not exists idx_student_outcomes_user on public.student_outcomes(user_id);
create index if not exists idx_student_outcomes_enrollment on public.student_outcomes(enrollment_decision_id);

-- =========================================================================
-- 3. TRIGGER FUNCTIONS  (defined BEFORE any CREATE TRIGGER)
-- =========================================================================

-- ---------------------------------------------------------------------------
-- Verification-level enforcement + stale-verified-claim guard.
-- Fires BEFORE INSERT or UPDATE on student_offers and student_awards.
--
-- Rules for an ORDINARY authenticated user (is_evidapath_trusted_role() = false):
--   * INSERT: verification_level is forced to 'self_reported' regardless of input.
--   * UPDATE: the student may NOT directly change verification_level at all
--     (any change raises an exception). Self-promotion is impossible.
--   * UPDATE: if the record was previously document_verified or
--     institution_verified AND a MATERIAL field changed, verification_level is
--     automatically reset to 'self_reported' so no verified claim stays stale.
--     Non-material user-only fields (e.g. notes) may be edited without reset.
--
-- A TRUSTED backend (service_role / admin, BYPASSRLS) may set any valid level
-- and edit freely — this is the future EvidaPath verification workflow path.
-- ---------------------------------------------------------------------------
create or replace function public.enforce_verification_level()
returns trigger language plpgsql as $$
declare
  prev_level      text;
  material_changed boolean := false;
begin
  -- Trusted EvidaPath backend (service role / admin) may set any valid level
  -- and edit any field freely.
  if public.is_evidapath_trusted_role() then
    return new;
  end if;

  -- Ordinary authenticated user:
  if tg_op = 'INSERT' then
    -- Students always start self_reported, regardless of what they send.
    new.verification_level := 'self_reported';
    return new;
  end if;

  -- UPDATE:
  -- 1. A student may NOT directly change verification_level at all.
  if new.verification_level is distinct from old.verification_level then
    raise exception
      'EvidaPath: verification_level can only be changed by a trusted EvidaPath verification process.';
  end if;

  -- 2. Stale-verified-claim guard: if the record was previously verified and a
  --    MATERIAL field changed, reset verification_level to self_reported.
  prev_level := old.verification_level;
  if prev_level in ('document_verified','institution_verified') then

    if tg_table_name = 'student_offers' then
      material_changed :=
        (new.application_id              is distinct from old.application_id)              or
        (new.admission_result            is distinct from old.admission_result)            or
        (new.official_offer_date         is distinct from old.official_offer_date)         or
        (new.response_deadline           is distinct from old.response_deadline)           or
        (new.enrollment_deposit_amount   is distinct from old.enrollment_deposit_amount)   or
        (new.deposit_deadline            is distinct from old.deposit_deadline)            or
        (new.currency                    is distinct from old.currency)                    or
        (new.conditions_of_admission     is distinct from old.conditions_of_admission);
    elsif tg_table_name = 'student_awards' then
      material_changed :=
        (new.offer_id           is distinct from old.offer_id)           or
        (new.sanity_scholarship_id is distinct from old.sanity_scholarship_id) or
        (new.award_name        is distinct from old.award_name)        or
        (new.award_type        is distinct from old.award_type)        or
        (new.amount            is distinct from old.amount)            or
        (new.currency          is distinct from old.currency)          or
        (new.frequency         is distinct from old.frequency)         or
        (new.duration_years    is distinct from old.duration_years)    or
        (new.renewal_criteria  is distinct from old.renewal_criteria)  or
        (new.min_gpa           is distinct from old.min_gpa)           or
        (new.need_vs_merit     is distinct from old.need_vs_merit)     or
        (new.document_id       is distinct from old.document_id);
    end if;

    if material_changed then
      new.verification_level := 'self_reported';
    end if;
  end if;

  return new;
end;
$$;

-- ---------------------------------------------------------------------------
-- SAME-OWNER GUARD: optional awards.document_id link.
-- A composite FK is awkward for an optional column, so this scoped trigger
-- verifies the referenced document belongs to the SAME user AND SAME offer.
-- Runs under the caller's RLS context: a document owned by another user is
-- invisible (RLS) -> not found -> exception.
-- ---------------------------------------------------------------------------
create or replace function public.enforce_award_document_owner()
returns trigger language plpgsql as $$
declare
  doc_user uuid;
  doc_offer uuid;
begin
  if new.document_id is not null then
    select user_id, offer_id
      into doc_user, doc_offer
      from public.student_offer_documents
      where id = new.document_id;

    if not found then
      raise exception
        'EvidaPath: referenced document does not exist or is not accessible.';
    end if;

    if doc_user is distinct from new.user_id
       or doc_offer is distinct from new.offer_id then
      raise exception
        'EvidaPath: award document must belong to the same user and offer.';
    end if;
  end if;
  return new;
end;
$$;

-- ---------------------------------------------------------------------------
-- SAME-OWNER GUARD: optional outcomes.enrollment_decision_id link.
-- Analogous to the awards.document_id guard. Verifies any non-null
-- enrollment_decision_id belongs to the SAME user_id.
-- ---------------------------------------------------------------------------
create or replace function public.enforce_outcome_enrollment_owner()
returns trigger language plpgsql as $$
declare
  dec_user uuid;
begin
  if new.enrollment_decision_id is not null then
    select user_id
      into dec_user
      from public.student_enrollment_decisions
      where id = new.enrollment_decision_id;

    if not found then
      raise exception
        'EvidaPath: referenced enrollment decision does not exist or is not accessible.';
    end if;

    if dec_user is distinct from new.user_id then
      raise exception
        'EvidaPath: enrollment decision must belong to the same user.';
    end if;
  end if;
  return new;
end;
$$;

-- ---------------------------------------------------------------------------
-- STORAGE-PATH OWNER GUARD for student_offer_documents.
-- storage_path MUST follow: <user-id>/<offer-id>/<file>
--   * segment 1 == owning user_id
--   * segment 2 == owning offer_id
--   * segment 3 (file portion) is non-empty
-- This agrees with the Storage policy convention (foldername()[1] == user id).
-- A student cannot attach metadata for Offer A to a file path under Offer B.
-- ---------------------------------------------------------------------------
create or replace function public.enforce_document_path_owner()
returns trigger language plpgsql as $$
declare
  seg1 text;
  seg2 text;
  file_part text;
begin
  if new.user_id is null then
    raise exception 'EvidaPath: document requires an owning user.';
  end if;

  seg1 := split_part(new.storage_path, '/', 1);
  seg2 := split_part(new.storage_path, '/', 2);
  file_part := split_part(new.storage_path, '/', 3);

  if seg1 is distinct from new.user_id::text then
    raise exception
      'EvidaPath: document storage_path must begin with your own user id folder (<user-id>/<offer-id>/<file>).';
  end if;

  if seg2 is distinct from new.offer_id::text then
    raise exception
      'EvidaPath: document storage_path second segment must match the owning offer id.';
  end if;

  if coalesce(file_part, '') = '' then
    raise exception
      'EvidaPath: document storage_path must include a file name after <user-id>/<offer-id>.';
  end if;

  return new;
end;
$$;

-- =========================================================================
-- 4. TRIGGERS  (all referenced functions now exist)
-- =========================================================================

-- updated_at triggers -------------------------------------------------------
drop trigger if exists trg_student_applications_updated on public.student_applications;
create trigger trg_student_applications_updated before update on public.student_applications
  for each row execute function public.set_updated_at();

drop trigger if exists trg_student_offers_updated on public.student_offers;
create trigger trg_student_offers_updated before update on public.student_offers
  for each row execute function public.set_updated_at();

drop trigger if exists trg_student_awards_updated on public.student_awards;
create trigger trg_student_awards_updated before update on public.student_awards
  for each row execute function public.set_updated_at();

-- verification-level + stale-claim guard triggers ---------------------------
-- Fire on ALL inserts/updates so material-field edits are caught (not just
-- edits to verification_level itself).
drop trigger if exists trg_student_offers_verification on public.student_offers;
create trigger trg_student_offers_verification
  before insert or update on public.student_offers
  for each row execute function public.enforce_verification_level();

drop trigger if exists trg_student_awards_verification on public.student_awards;
create trigger trg_student_awards_verification
  before insert or update on public.student_awards
  for each row execute function public.enforce_verification_level();

-- optional-link ownership triggers ------------------------------------------
-- Fires on document_id, offer_id AND user_id so the same-user/same-offer
-- invariant is rechecked whenever any of those columns changes. Changing
-- offer_id while leaving document_id unchanged would otherwise let an award
-- point at a document belonging to a different offer.
drop trigger if exists trg_student_awards_document_owner on public.student_awards;
create trigger trg_student_awards_document_owner
  before insert or update of document_id, offer_id, user_id on public.student_awards
  for each row execute function public.enforce_award_document_owner();

-- Fires on enrollment_decision_id AND user_id so ownership is rechecked if
-- either column changes.
drop trigger if exists trg_student_outcomes_enrollment_owner on public.student_outcomes;
create trigger trg_student_outcomes_enrollment_owner
  before insert or update of enrollment_decision_id, user_id on public.student_outcomes
  for each row execute function public.enforce_outcome_enrollment_owner();

-- storage-path guard trigger ------------------------------------------------
drop trigger if exists trg_student_offer_documents_path on public.student_offer_documents;
create trigger trg_student_offer_documents_path
  before insert or update of storage_path, offer_id, user_id on public.student_offer_documents
  for each row execute function public.enforce_document_path_owner();

-- =========================================================================
-- 5. ROW LEVEL SECURITY
-- =========================================================================

alter table public.student_applications          enable row level security;
alter table public.student_offers                enable row level security;
alter table public.student_awards                enable row level security;
alter table public.student_offer_documents       enable row level security;
alter table public.student_enrollment_decisions  enable row level security;
alter table public.student_outcomes              enable row level security;

-- student_applications
drop policy if exists "student_applications_select_own" on public.student_applications;
create policy "student_applications_select_own" on public.student_applications
  for select to authenticated
  using (auth.uid() is not null and user_id = auth.uid());

drop policy if exists "student_applications_insert_own" on public.student_applications;
create policy "student_applications_insert_own" on public.student_applications
  for insert to authenticated
  with check (auth.uid() is not null and user_id = auth.uid());

drop policy if exists "student_applications_update_own" on public.student_applications;
create policy "student_applications_update_own" on public.student_applications
  for update to authenticated
  using (auth.uid() is not null and user_id = auth.uid())
  with check (auth.uid() is not null and user_id = auth.uid());

drop policy if exists "student_applications_delete_own" on public.student_applications;
create policy "student_applications_delete_own" on public.student_applications
  for delete to authenticated
  using (auth.uid() is not null and user_id = auth.uid());

-- student_offers
drop policy if exists "student_offers_all_own" on public.student_offers;
create policy "student_offers_all_own" on public.student_offers
  for all to authenticated
  using (auth.uid() is not null and user_id = auth.uid())
  with check (auth.uid() is not null and user_id = auth.uid());

-- student_awards
drop policy if exists "student_awards_all_own" on public.student_awards;
create policy "student_awards_all_own" on public.student_awards
  for all to authenticated
  using (auth.uid() is not null and user_id = auth.uid())
  with check (auth.uid() is not null and user_id = auth.uid());

-- student_offer_documents
drop policy if exists "student_offer_documents_all_own" on public.student_offer_documents;
create policy "student_offer_documents_all_own" on public.student_offer_documents
  for all to authenticated
  using (auth.uid() is not null and user_id = auth.uid())
  with check (auth.uid() is not null and user_id = auth.uid());

-- student_enrollment_decisions
drop policy if exists "student_enrollment_decisions_all_own" on public.student_enrollment_decisions;
create policy "student_enrollment_decisions_all_own" on public.student_enrollment_decisions
  for all to authenticated
  using (auth.uid() is not null and user_id = auth.uid())
  with check (auth.uid() is not null and user_id = auth.uid());

-- student_outcomes
drop policy if exists "student_outcomes_all_own" on public.student_outcomes;
create policy "student_outcomes_all_own" on public.student_outcomes
  for all to authenticated
  using (auth.uid() is not null and user_id = auth.uid())
  with check (auth.uid() is not null and user_id = auth.uid());

-- =========================================================================
-- 6. STORAGE — private bucket for student offer/award documents
-- Files are PRIVATE. No public URLs. Signed/authenticated URLs only.
--
-- Path convention: <auth-user-id>/<offer-id>/<file>
--   e.g. 550e8400-e29b-41d4-a716-446655440000/<offer-id>/scholarship-letter.pdf
--
-- Policies use the current Supabase Storage ownership model:
--   * owner_id compared as TEXT  ->  owner_id::text = (select auth.uid()::text)
--   * storage.foldername(name) returns a TEXT ARRAY; the first segment is
--     (storage.foldername(name))[1], required to equal the auth user id.
-- Both checks are applied (defense in depth) on SELECT/INSERT/UPDATE/DELETE.
-- =========================================================================
insert into storage.buckets (id, name, public)
values ('student-documents', 'student-documents', false)
on conflict (id) do nothing;

-- READ (select + list): only the owner, only inside their own folder
drop policy if exists "student_docs_read_own" on storage.objects;
create policy "student_docs_read_own" on storage.objects
  for select to authenticated
  using (
    bucket_id = 'student-documents'
    and auth.uid() is not null
    and owner_id::text = (select auth.uid()::text)
    and (storage.foldername(name))[1] = (select auth.uid()::text)
  );

-- INSERT: must own the object AND place it under their own user folder
drop policy if exists "student_docs_write_own" on storage.objects;
create policy "student_docs_write_own" on storage.objects
  for insert to authenticated
  with check (
    bucket_id = 'student-documents'
    and auth.uid() is not null
    and owner_id::text = (select auth.uid()::text)
    and (storage.foldername(name))[1] = (select auth.uid()::text)
  );

-- UPDATE: only the owner, only inside their own folder
drop policy if exists "student_docs_update_own" on storage.objects;
create policy "student_docs_update_own" on storage.objects
  for update to authenticated
  using (
    bucket_id = 'student-documents'
    and auth.uid() is not null
    and owner_id::text = (select auth.uid()::text)
    and (storage.foldername(name))[1] = (select auth.uid()::text)
  )
  with check (
    bucket_id = 'student-documents'
    and auth.uid() is not null
    and owner_id::text = (select auth.uid()::text)
    and (storage.foldername(name))[1] = (select auth.uid()::text)
  );

-- DELETE: only the owner, only inside their own folder
drop policy if exists "student_docs_delete_own" on storage.objects;
create policy "student_docs_delete_own" on storage.objects
  for delete to authenticated
  using (
    bucket_id = 'student-documents'
    and auth.uid() is not null
    and owner_id::text = (select auth.uid()::text)
    and (storage.foldername(name))[1] = (select auth.uid()::text)
  );

-- =========================================================================
-- DONE — final revised migration (awaiting approval; do NOT run automatically)
--
-- Tables: student_applications, student_offers, student_awards,
--         student_offer_documents, student_enrollment_decisions, student_outcomes
-- Storage bucket: student-documents (private)
-- RLS: enabled on all tables + storage bucket (TO authenticated, owner = auth.uid())
-- Same-owner integrity: composite FKs + scoped triggers (awards.document_id,
--                        outcomes.enrollment_decision_id)
-- Verification lock: enforce_verification_level() on offers + awards
--                     (no self-promotion; material edits reset to self_reported)
-- Storage path: <user-id>/<offer-id>/<file> enforced at DB + policy level
-- =========================================================================
