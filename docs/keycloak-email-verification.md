# Keycloak Email Verification Guide

This guide explains how to configure Keycloak email for the local
`admin-starter` realm so you can test email verification, registration emails,
and forgot-password emails.

Use this alongside [keycloak-setup.md](keycloak-setup.md).

## Resend SMTP

Use Resend when you want Keycloak to send real verification emails.

Before configuring Keycloak:

1. Create or open your Resend account.
2. Verify your sending domain in Resend.
3. Create a Resend API key.
4. Choose a sender address from the verified domain, for example:

   ```text
   no-reply@example.com
   ```

In the Keycloak admin console:

1. Select the `admin-starter` realm.
2. Go to **Realm settings**.
3. Open the **Email** tab.
4. Use these values:

   ```text
   From: no-reply@example.com
   From display name: Admin Starter
   Reply to: support@example.com
   Host: smtp.resend.com
   Port: 587
   Enable SSL: Off
   Enable StartTLS: On
   Authentication: On
   Username: resend
   Password: <your Resend API key>
   ```

5. Save.
6. Click **Test connection**.

If port `587` is blocked by your network or host, use Resend's implicit TLS
option instead:

```text
Port: 465
Enable SSL: On
Enable StartTLS: Off
Authentication: On
Username: resend
Password: <your Resend API key>
```

The Resend API key is the SMTP password. Do not use your Resend account
password, and do not commit the API key to the repository.

## Local Test Mailbox

For local development, use a fake SMTP inbox instead of a real email provider.
Mailpit accepts SMTP messages and shows them in a browser UI.

Start Mailpit from the project root:

```bash
docker run --rm -d --name app-mailpit -p 1025:1025 -p 8025:8025 axllent/mailpit:latest
```

Open the local mailbox:

```text
http://localhost:8025
```

Keycloak runs inside Docker. On Docker Desktop for Windows, Keycloak can reach
the host-published Mailpit SMTP port through:

```text
host.docker.internal
```

Stop Mailpit when you are done:

```bash
docker stop app-mailpit
```

## Start Keycloak

Use either local mode:

```bash
corepack pnpm db:up
corepack pnpm auth:up
```

Open:

```text
http://localhost:8080
```

Or use Traefik mode:

```bash
corepack pnpm dev:gateway
```

Open:

```text
http://auth.localhost
```

Sign in with `KEYCLOAK_ADMIN_USER` and `KEYCLOAK_ADMIN_PASSWORD`.

## Configure Mailpit SMTP

In the Keycloak admin console:

1. Select the `admin-starter` realm.
2. Go to **Realm settings**.
3. Open the **Email** tab.
4. Set the local SMTP values:

   ```text
   From: no-reply@admin-starter.local
   From display name: Admin Starter
   Reply to: no-reply@admin-starter.local
   Host: host.docker.internal
   Port: 1025
   Encryption: None
   Authentication: Off
   ```

5. Save.
6. Click **Test connection**.

If the test succeeds, a message should appear in Mailpit at:

```text
http://localhost:8025
```

## Enable Email Verification

In the `admin-starter` realm:

1. Go to **Realm settings**.
2. Open the **Login** tab.
3. Turn **Verify email** on.
4. Turn **Forgot password** on if you also want to test password reset.
5. Keep **Login with email** on.
6. Keep **Duplicate emails** off.
7. Save.

For public self-service registration tests:

1. Stay on **Realm settings**.
2. Open the **Login** tab.
3. Turn **User registration** on.
4. Save.

Keep registration off for private/internal deployments unless public signup is
an intentional product choice.

## Test With An Existing User

Create or update a test user:

1. Go to **Users**.
2. Open an existing test user or choose **Create new user**.
3. Set a real-looking email, for example:

   ```text
   test-user@example.local
   ```

4. Set **Email verified** to off.
5. Save.
6. Open **Credentials**.
7. Set a password for the user.
8. Disable **Temporary** if you do not want to test the forced password-change
   flow at the same time.

Send a verification email:

1. Open the user.
2. Use the user action menu.
3. Choose **Send verify email**.
4. Open the destination inbox.
   - For Resend, open the email inbox for that test address.
   - For Mailpit, open `http://localhost:8025`.
5. Open the email and click the verification link.

After the link opens in Keycloak, return to the user in the admin console and
confirm **Email verified** is on.

## Test Through Login

With **Verify email** on, an unverified user is blocked from normal app access
until their email is verified.

1. Make sure Mailpit is running.
2. Make sure the user has **Email verified** off.
3. Open the app:

   ```text
   http://localhost:5173
   ```

   Or in Traefik mode:

   ```text
   http://app.localhost
   ```

4. Choose login.
5. Sign in with the unverified user.
6. Keycloak should require email verification before completing login.
7. Open the destination inbox, click the verification link, then continue the
   login flow.

If the app silently signs in as a different user, use the visible Login button
or visit:

```text
http://localhost:5173/auth/login?prompt=login
```

In Traefik mode:

```text
http://app.localhost/auth/login?prompt=login
```

## Test Registration

Use this only when **User registration** is on.

1. Open the app.
2. Choose Register.
3. Complete the Keycloak registration form with a test email.
4. Open the destination inbox.
5. Click the verification link.
6. Confirm the user can finish login after verification.

The app's Register button sends users to Keycloak. The React app should not
implement its own registration form.

## Test Forgot Password

Forgot-password emails require working SMTP.

1. Go to the Keycloak login page.
2. Choose **Forgot password**.
3. Enter the test user's username or email.
4. Open the destination inbox.
5. Click the password reset link.
6. Set the new password.
7. Sign in again.

## Other SMTP Providers

For production or shared staging, use a real transactional email provider such
as Resend instead of Mailpit.

Typical SMTP settings:

```text
Host: smtp.example.com
Port: 587
Encryption: StartTLS
Authentication: On
Username: <smtp-username>
Password: <smtp-password>
From: no-reply@example.com
From display name: Admin Starter
Reply to: support@example.com
```

Provider notes:

- Prefer port `587` with StartTLS for most SMTP providers.
- Use port `465` only when the provider explicitly requires SSL/TLS.
- Use a dedicated transactional email credential, not a personal inbox
  password.
- Verify the sender domain with SPF, DKIM, and DMARC before production use.
- Do not commit SMTP credentials to the repository.

Keycloak stores realm SMTP settings in its database. For production, manage
these settings through a controlled admin process, Terraform once added, or a
deployment secret workflow. Treat realm exports and Terraform state as
sensitive if they can contain provider details.

## Troubleshooting

If **Test connection** fails:

- If using Mailpit, confirm Mailpit is running:

  ```bash
  docker ps --filter name=app-mailpit
  ```

- If using Mailpit, confirm the SMTP host is `host.docker.internal`, not
  `localhost`. From inside the Keycloak container, `localhost` means the
  Keycloak container itself.
- If using Mailpit, confirm the SMTP port is `1025`.
- If using Mailpit, confirm encryption is off and authentication is off.
- If using Resend, confirm outbound SMTP traffic is allowed from the machine
  running Keycloak.
- If using Resend, try port `465` with SSL on if port `587` with StartTLS fails.
- Restart Keycloak after changing Docker networking or local firewall settings.

If no verification email appears:

- Confirm you selected the `admin-starter` realm before configuring email.
- Confirm the user has an email address.
- Confirm **Email verified** is off before sending the verification email.
- For Resend, confirm the `From` address belongs to a verified sending domain.
- For Resend, confirm the SMTP username is the literal value `resend`.
- For Resend, confirm the SMTP password is the API key, not your dashboard
  login password.
- Check Keycloak logs:

  ```bash
  corepack pnpm auth:logs
  ```

  Or in Traefik mode:

  ```bash
  corepack pnpm auth:gateway:logs
  ```

If the verification link opens the wrong host:

- Direct local mode should use:

  ```text
  KEYCLOAK_HOSTNAME=localhost
  KEYCLOAK_EXTERNAL_URL=http://localhost:8080
  ```

- Traefik mode should use:

  ```text
  KEYCLOAK_EXTERNAL_URL=http://auth.localhost
  KEYCLOAK_ISSUER=http://auth.localhost/realms/admin-starter
  ```

- Restart Keycloak after changing hostname-related environment values.

## References

- Local Keycloak setup:
  [keycloak-setup.md](keycloak-setup.md)
- Keycloak server administration:
  <https://www.keycloak.org/docs/latest/server_admin/>
- Resend SMTP:
  <https://resend.com/docs/send-with-smtp>
- Mailpit:
  <https://mailpit.axllent.org/>
