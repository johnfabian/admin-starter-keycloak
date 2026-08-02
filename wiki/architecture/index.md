# Architecture

## Concepts

- [Access control model](access-control-model.md) - Implemented role resolution and guarded-route authorization in the BFF.
- [Gateway network model](gateway-network-model.md) - Public and internal Docker network placement in gateway mode.
- [Gateway routing](gateway-routing.md) - Implemented host-based routing through the local Traefik edge.
- [Known production gaps](known-production-gaps.md) - Evidence-backed absences and defects that block a production claim.
- [Repository implementation boundaries](repository-boundaries.md) - Distinguishes runnable application code, infrastructure, and documented placeholders.
- [React Router BFF](react-router-bff.md) - Describes the implemented browser-facing authentication and session boundary.
- [Realm export versus backup](realm-export-vs-backup.md) - Separates reviewable Keycloak configuration from recoverable database state.
- [Registration approval SPI](registration-approval-spi.md) - Custom listener behavior for verified self-registered users.
