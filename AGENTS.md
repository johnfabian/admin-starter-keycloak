# Repository Rules

- Use `.server.ts` for server-only modules and `.client.ts` for browser-only modules.
- Avoid magic strings and numbers in application code. Promote repeated, security-sensitive, protocol, header, storage-key, and configuration values to named constants or shared config.
- Keep SQL in repository/data-access modules, not in auth, UI, route, or service files.
- Keep browser code free of Keycloak access and refresh tokens; the React Router server remains the BFF boundary.
