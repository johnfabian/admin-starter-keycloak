-- Runs once on first container boot via docker-entrypoint-initdb.d.
-- Creates application-owned tables in POSTGRES_DB.
CREATE TABLE IF NOT EXISTS web_bff_sessions (
  id text PRIMARY KEY,
  user_id text NOT NULL,
  user_data jsonb NOT NULL,
  token_payload text NOT NULL,
  access_token_expires_at timestamptz NOT NULL,
  refresh_token_expires_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  last_seen_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_web_bff_sessions_user_id
  ON web_bff_sessions (user_id);

CREATE INDEX IF NOT EXISTS idx_web_bff_sessions_refresh_token_expires_at
  ON web_bff_sessions (refresh_token_expires_at);
