-- Least-privilege hardening for student tables (2026-10-29).
--
-- anon and authenticated held TRUNCATE, TRIGGER and REFERENCES on every
-- student table. TRUNCATE is not subject to Row Level Security, so a role
-- holding it could wipe every student's rows at once. PostgREST does not
-- expose TRUNCATE, but the grant served no purpose and widened the blast
-- radius of any future SQL-execution path. The app only needs
-- SELECT/INSERT/UPDATE/DELETE, which stay in place and remain RLS-scoped.
--
-- Rollback: GRANT TRUNCATE, TRIGGER, REFERENCES ON <table> TO anon, authenticated;

revoke truncate, trigger, references on
  public.student_applications,
  public.student_awards,
  public.student_enrollment_decisions,
  public.student_offer_documents,
  public.student_offers,
  public.student_outcomes,
  public.student_profiles,
  public.student_saved_universities
from anon, authenticated;
