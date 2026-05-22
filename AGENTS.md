# Repository Rules

## Git Workflow

- Never make code changes directly on `master`. Create or switch to a feature branch before editing files.

## File Naming

- Use `.server.ts` for server-only modules.
- Use `.client.ts` for browser-only modules.
- Use `.shared.ts` for modules that are safe on both server and client.

## Code Quality

- Avoid magic strings and numbers in application code.
- Promote repeated, security-sensitive, protocol, header, storage-key, and configuration values to named constants or shared config.

## Data Access

- Keep SQL in repository/data-access modules, not in auth, UI, route, or service files.

## Security

- Keep browser code free of Keycloak access and refresh tokens.
- Keep the React Router server as the BFF boundary.
- Do not add inline executable scripts, embedded JavaScript, or `dangerouslySetInnerHTML`.

## Error Handling

- Route errors should render reusable error UI instead of raw text responses.
- Recoverable auth and session failures should clear session state and redirect to login.
- Logout must clear the local browser cookie even if downstream cleanup fails.
- Normalize Keycloak, token, and network failures before they reach UI.
- Never expose tokens, raw stack traces, or sensitive backend details to browser UI.
