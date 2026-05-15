# Keycloak Terraform Guide

This guide explains how to manage Keycloak configuration with Terraform for
this project. Use it alongside [keycloak-setup.md](keycloak-setup.md) and
[keycloak-roles-and-permissions.md](keycloak-roles-and-permissions.md).

Terraform is useful for making Keycloak configuration repeatable:

- realms
- clients
- redirect URIs
- client roles
- groups
- group role mappings
- client scopes
- protocol mappers
- organizations
- identity providers

Terraform does not replace database backups. It records intended configuration,
not live user sessions, events, revoked tokens, or every operational data point
inside Keycloak.

## Current State

This repository does not currently contain Terraform configuration. Keycloak
settings made in the admin console are stored in the Keycloak Postgres database,
inside the Docker volume used by the Compose stack.

The repo currently stores:

- Docker Compose files for Keycloak and Postgres
- environment variable examples
- documentation for the desired Keycloak setup

The repo does not currently store:

- live realm settings
- users
- client secrets
- Keycloak database data
- Terraform state

## Provider

Use the official Keycloak Terraform provider:

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    keycloak = {
      source  = "keycloak/keycloak"
      version = ">= 5.7.0"
    }
  }
}
```

The older `mrparkers/keycloak` provider was moved under the Keycloak
organization. New work should use `keycloak/keycloak`.

## Recommended Directory Layout

When Terraform is added, keep it isolated from app code:

```text
infra/
  keycloak/
    README.md
    versions.tf
    providers.tf
    variables.tf
    locals.tf
    realm.tf
    clients.tf
    roles.tf
    groups.tf
    client-scopes.tf
    organizations.tf
    outputs.tf
    envs/
      local.tfvars.example
      prod.tfvars.example
```

Commit `.tf` files and non-secret example `.tfvars` files. Do not commit local
state, local plans, or secret variable files.

This repo already ignores local Terraform state, plans, and secret variable
files:

```gitignore
# Terraform
**/.terraform/
*.tfstate
*.tfstate.*
*.tfvars
!*.tfvars.example
*.tfplan
crash.log
crash.*.log
override.tf
override.tf.json
*_override.tf
*_override.tf.json
```

## Provider Authentication

For local development, use a dedicated Terraform admin client or a short-lived
admin user credential.

Example provider shape:

```hcl
provider "keycloak" {
  url       = var.keycloak_url
  realm     = "master"
  client_id = var.keycloak_admin_client_id
  username  = var.keycloak_admin_username
  password  = var.keycloak_admin_password
}
```

Example local variables:

```hcl
keycloak_url                = "http://localhost:8080"
keycloak_admin_client_id    = "admin-cli"
keycloak_admin_username     = "admin"
keycloak_admin_password     = "change-me-local"
```

For the local Traefik stack, point Terraform at:

```hcl
keycloak_url = "http://auth.localhost"
```

For production, do not use a personal admin user. Prefer a dedicated automation
client with the minimum required realm-management roles. Store credentials in a
secret manager or CI/CD secret store.

## Example Realm

```hcl
resource "keycloak_realm" "admin_starter" {
  realm   = var.realm_name
  enabled = true

  display_name = "Admin Starter"

  registration_allowed           = var.registration_allowed
  registration_email_as_username = false
  login_with_email_allowed       = true
  duplicate_emails_allowed       = false
  verify_email                   = var.verify_email
  reset_password_allowed         = true
  remember_me                    = false
  brute_force_protected          = true

  sso_session_idle_timeout = "30m"
  sso_session_max_lifespan = "8h"
  access_token_lifespan    = "5m"
}
```

Exact argument names can change by provider version. Treat the examples in this
doc as starting points and confirm resource arguments against the provider
registry when implementing.

## Example Clients

### React Router Web Client

```hcl
resource "keycloak_openid_client" "web" {
  realm_id  = keycloak_realm.admin_starter.id
  client_id = "admin-starter-web"
  name      = "Admin Starter Web"
  enabled   = true

  access_type              = "PUBLIC"
  standard_flow_enabled    = true
  implicit_flow_enabled    = false
  direct_access_grants_enabled = false
  service_accounts_enabled = false

  root_url = var.web_root_url
  base_url = var.web_root_url

  valid_redirect_uris = [
    "${var.web_root_url}/*",
    "${var.web_root_url}/auth/callback",
  ]

  valid_post_logout_redirect_uris = [
    "${var.web_root_url}/*",
  ]

  web_origins = [
    var.web_root_url,
  ]

  pkce_code_challenge_method = "S256"
}
```

Local values:

```hcl
web_root_url = "http://app.localhost"
```

Production values:

```hcl
web_root_url = "https://app.example.com"
```

### FastAPI API Client

```hcl
resource "keycloak_openid_client" "api" {
  realm_id  = keycloak_realm.admin_starter.id
  client_id = "admin-starter-api"
  name      = "Admin Starter API"
  enabled   = true

  access_type                  = "PUBLIC"
  standard_flow_enabled        = false
  implicit_flow_enabled        = false
  direct_access_grants_enabled = false
  service_accounts_enabled     = false

  root_url = var.api_root_url
  base_url = var.api_root_url
}
```

Local values:

```hcl
api_root_url = "http://api.localhost"
```

Production values:

```hcl
api_root_url = "https://api.example.com"
```

### Expo Mobile Client

```hcl
resource "keycloak_openid_client" "mobile" {
  realm_id  = keycloak_realm.admin_starter.id
  client_id = "admin-starter-mobile"
  name      = "Admin Starter Mobile"
  enabled   = true

  access_type                  = "PUBLIC"
  standard_flow_enabled        = true
  implicit_flow_enabled        = false
  direct_access_grants_enabled = false
  service_accounts_enabled     = false

  valid_redirect_uris = [
    "adminstarter://auth/callback",
    "adminstarter:///auth/callback",
    "com.yourcompany.adminstarter://auth/callback",
  ]

  valid_post_logout_redirect_uris = [
    "adminstarter://auth/logout",
    "adminstarter:///auth/logout",
  ]

  pkce_code_challenge_method = "S256"
}
```

## Example Roles And Groups

```hcl
resource "keycloak_role" "web_users" {
  realm_id  = keycloak_realm.admin_starter.id
  client_id = keycloak_openid_client.web.id
  name      = "Users"
}

resource "keycloak_role" "web_admins" {
  realm_id  = keycloak_realm.admin_starter.id
  client_id = keycloak_openid_client.web.id
  name      = "Admins"
}

resource "keycloak_role" "api_users" {
  realm_id  = keycloak_realm.admin_starter.id
  client_id = keycloak_openid_client.api.id
  name      = "api-users"
}

resource "keycloak_role" "api_admins" {
  realm_id  = keycloak_realm.admin_starter.id
  client_id = keycloak_openid_client.api.id
  name      = "api-admins"
}

resource "keycloak_group" "application_users" {
  realm_id = keycloak_realm.admin_starter.id
  name     = "Application Users"
}

resource "keycloak_group" "application_admins" {
  realm_id = keycloak_realm.admin_starter.id
  name     = "Application Admins"
}
```

Group role mappings are provider resources too. Wire groups to roles so humans
are assigned to groups, not directly to roles.

## Example API Audience Scope

The web and mobile clients should receive an API audience claim so FastAPI can
validate that the token was intended for the API.

Desired outcome:

```json
{
  "aud": ["admin-starter-api"]
}
```

Terraform should manage:

- a client scope named `admin-starter-api-audience`
- an audience protocol mapper that adds `admin-starter-api`
- default client scope assignment for `admin-starter-web`
- default client scope assignment for `admin-starter-mobile`

Provider resource names for protocol mappers are version-specific. Confirm the
exact resource names in the provider registry before implementing.

## Organizations

The official provider supports `keycloak_organization`.

Example shape:

```hcl
resource "keycloak_organization" "acme" {
  realm   = keycloak_realm.admin_starter.name
  name    = "Acme"
  alias   = "acme"
  enabled = true

  domain {
    name     = "acme.example.com"
    verified = false
  }
}
```

Organization aliases should be stable. If a customer changes its display name,
change the display name rather than the alias used in URLs, tokens, and app
data.

## Importing Existing Manual Config

If you already configured Keycloak through the admin console, do not blindly
apply Terraform over it. First choose a migration path:

1. Export a realm snapshot for reference.
2. Write Terraform to match the existing config.
3. Import existing resources into Terraform state.
4. Run `terraform plan`.
5. Review every proposed change.
6. Apply only after the plan shows expected changes.

Common importable resources:

- realm
- clients
- roles
- groups
- client scopes
- protocol mappers
- organizations

The exact import ID format depends on the resource. Check the provider docs for
each resource.

## State And Secrets

Terraform state can contain sensitive values, including generated client
secrets, provider credentials, or mapper details. Treat state as sensitive.

Do:

- use an encrypted remote backend for shared work
- restrict state access
- store provider credentials in CI/CD secrets or a secret manager
- commit `.tf` code
- commit `.tfvars.example` files with fake values

Do not:

- commit `terraform.tfstate`
- commit real `.tfvars`
- commit client secrets
- use a personal admin account in production automation

## Local Workflow

Example once `infra/keycloak` exists:

```bash
cd infra/keycloak
terraform init
terraform fmt -recursive
terraform validate
terraform plan -var-file ./envs/local.tfvars
terraform apply -var-file ./envs/local.tfvars
```

Run Terraform against local direct Keycloak:

```hcl
keycloak_url = "http://localhost:8080"
```

Run Terraform against local Traefik Keycloak:

```hcl
keycloak_url = "http://auth.localhost"
```

## Production Workflow

Production Terraform should run through CI/CD or a controlled admin machine.

Recommended gates:

1. `terraform fmt -check -recursive`
2. `terraform validate`
3. `terraform plan`
4. Human review of the plan
5. `terraform apply`
6. Smoke test login and token claims
7. Record the applied commit SHA and state version

For production, separate environment values:

```hcl
realm_name   = "admin-starter-prod"
web_root_url = "https://app.example.com"
api_root_url = "https://api.example.com"
```

## Terraform Vs Realm Export Vs Database Backup

| Tool            | Best For                           | Not Good For                               |
| --------------- | ---------------------------------- | ------------------------------------------ |
| Terraform       | Desired Keycloak config in Git     | Live sessions, events, point-in-time data  |
| Realm export    | Human-readable config snapshot     | Complete backup/restore                    |
| Postgres backup | Disaster recovery and full restore | Reviewing intended config in pull requests |

Use Terraform for repeatability. Use Postgres backups for recovery. Use realm
exports as a convenient snapshot after major admin-console changes.

## References

- Keycloak Terraform provider:
  <https://github.com/keycloak/terraform-provider-keycloak>
- Terraform Registry provider docs:
  <https://registry.terraform.io/providers/keycloak/keycloak/latest/docs>
- Keycloak organization Terraform resource:
  <https://registry.terraform.io/providers/keycloak/keycloak/latest/docs/resources/organization>
- Keycloak import/export docs:
  <https://www.keycloak.org/server/importExport>
- Local roles and permissions guide:
  [keycloak-roles-and-permissions.md](keycloak-roles-and-permissions.md)
