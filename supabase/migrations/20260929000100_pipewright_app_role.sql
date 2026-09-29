-- Least-privilege login used by the Vercel backend (DATABASE_URL user: pipewright_app.<project-ref>).
-- The real password was set out-of-band with ALTER ROLE and lives only in Vercel's env vars.
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'pipewright_app') THEN
    CREATE ROLE pipewright_app LOGIN PASSWORD NULL;
  END IF;
END $$;
GRANT USAGE ON SCHEMA public TO pipewright_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON campaigns, prospects, messages, replies, suppression, ledger TO pipewright_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO pipewright_app;
-- RLS stays on: only this role gets a policy; Supabase's anon/authenticated API roles get none.
DO $$ DECLARE t text; BEGIN
  FOREACH t IN ARRAY ARRAY['campaigns','prospects','messages','replies','suppression','ledger'] LOOP
    EXECUTE format('DROP POLICY IF EXISTS app_all ON %I', t);
    EXECUTE format('CREATE POLICY app_all ON %I FOR ALL TO pipewright_app USING (true) WITH CHECK (true)', t);
  END LOOP;
END $$;
