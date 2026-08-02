---
type: Schema
title: Web BFF sessions
description: Postgres storage schema and repository boundary for React Router BFF session records.
resource: /postgres/init-app-schema.sql
tags: [postgres, sessions, bff, tokens]
status: draft
generated: { by: codex/gpt-5, at: 2026-08-02T15:45:23Z }
stale_after: 2026-11-02
sources:
  - id: schema-sql
    resource: /postgres/init-app-schema.sql
    title: Application schema initialization SQL
    last_modified: 2026-05-21
  - id: session-repository
    resource: /web/app/lib/server/data/bff-session.repository.server.ts
    title: BFF session data-access repository
    last_modified: 2026-05-21
  - id: postgres-compose
    resource: /postgres/docker-compose.yml
    title: Direct-development Postgres Compose configuration
    last_modified: 2026-05-21
---

# Schema

`web_bff_sessions` stores a text primary key, user identifier, JSON user data, encrypted token payload text, access/refresh expiry timestamps, and created/updated/last-seen timestamps.[^schema-sql] Indexes exist for `user_id` and `refresh_token_expires_at`.[^schema-sql]

The TypeScript repository under `web/app/lib/server/data/` owns insert, lookup, touch, update, and delete SQL for this table.[^session-repository]

# Lifecycle constraint

The SQL file is mounted under `/docker-entrypoint-initdb.d/`, so it runs when a new Postgres data volume is initialized rather than as a general migration runner.[^postgres-compose] Schema changes therefore need an explicit migration/application plan for existing volumes.

# Related concepts

- [React Router BFF](/architecture/react-router-bff.md)

# Uncertainty

The repository has no migration framework or automated schema test. Retention, cleanup, capacity, and production backup expectations for BFF sessions are not defined by the implemented schema.

[^schema-sql]: Application schema initialization SQL

[^session-repository]: BFF session data-access repository

[^postgres-compose]: Direct-development Postgres Compose configuration
