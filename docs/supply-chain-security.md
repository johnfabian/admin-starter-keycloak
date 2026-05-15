# Supply Chain Security

This repo uses pnpm because recent npm ecosystem attacks have abused dependency
install behavior, maintainer token compromise, and fast-moving malicious
package releases.

## Threat Model

The main risks this repo is trying to reduce are:

- compromised npm packages published under trusted package names
- install lifecycle scripts that run automatically during dependency install
- malicious packages that are detected and removed shortly after publication
- transitive dependencies pulled from git repositories or tarball URLs
- lockfile changes that quietly introduce unexpected package versions

CISA published an alert in September 2025 for a widespread npm supply-chain
compromise involving the Shai-Hulud campaign. pnpm's current supply-chain
guidance specifically calls out delaying dependency updates, blocking risky
postinstall scripts, preventing exotic transitive dependencies, and committing
the lockfile.

This is still active risk in 2026. SANS documented a March 31, 2026 Axios npm
compromise where poisoned package versions executed during install and targeted
developer, CI/CD, and production rebuild environments.

## Repo Settings

The root `pnpm-workspace.yaml` includes:

```yaml
minimumReleaseAge: 10080
minimumReleaseAgeStrict: true
minimumReleaseAgeIgnoreMissingTime: false
blockExoticSubdeps: true
strictDepBuilds: true
trustPolicy: no-downgrade
allowBuilds:
  esbuild: false
```

### `minimumReleaseAge: 10080`

Only install package versions that are at least 7 days old. pnpm 11 defaults to
1 day, but this repo uses a longer delay because it is a starter project and
does not need same-day dependency releases.

### `minimumReleaseAgeStrict: true`

Fail dependency resolution instead of falling back to a too-new version.

### `minimumReleaseAgeIgnoreMissingTime: false`

Fail if registry metadata does not include publish time information. This keeps
the delay policy enforceable.

### `blockExoticSubdeps: true`

Prevent transitive dependencies from resolving from git repositories or direct
tarball URLs. Direct dependencies can still use explicit non-registry sources if
the repo owner intentionally adds them.

### `strictDepBuilds: true`

Fail installs when a dependency has an unreviewed install/build script.

### `allowBuilds`

pnpm 11 uses `allowBuilds` to explicitly allow or deny dependency lifecycle
scripts. This repo currently denies `esbuild` install scripts:

```yaml
allowBuilds:
  esbuild: false
```

The current web app still builds successfully with this denied because the
needed platform package is installed without running the package lifecycle
script.

If a future dependency truly needs an install script, review it first, then add
only that package:

```yaml
allowBuilds:
  package-name: true
```

You can inspect pending ignored builds with:

```bash
pnpm ignored-builds
```

You can use pnpm's guided approval flow with:

```bash
pnpm approve-builds
```

## Daily Workflow

Use the pinned pnpm version:

```bash
pnpm install
pnpm check
```

Review every `pnpm-lock.yaml` change in pull requests. A lockfile change is a
supply-chain change, even if no direct dependency was edited.

Prefer adding dependencies intentionally:

```bash
pnpm --dir web add package-name
pnpm --dir web add -D package-name
```

Avoid:

```bash
pnpm update --latest
```

unless the update is intentional and the lockfile diff is reviewed.

## If An Install Fails

For a package that is too new:

1. Wait until it passes the release-age window.
2. Pin an older safe version.
3. Use `minimumReleaseAgeExclude` only for a reviewed emergency.

For a package with an install script:

1. Run `pnpm ignored-builds`.
2. Check why the package needs a lifecycle script.
3. Prefer `allowBuilds: package-name: false` when the app still works.
4. Use `allowBuilds: package-name: true` only after review.

For a trust policy failure:

1. Investigate why the package lost trusted-publishing/provenance evidence.
2. Prefer waiting or pinning an older known-good version.
3. Use `trustPolicyExclude` only for a reviewed exception.

## GitHub And npm Account Hygiene

Repo settings help, but they do not replace account security:

- enable MFA on GitHub and npm accounts
- do not store npm tokens or cloud credentials in local env files
- rotate tokens after any suspicious install
- avoid long-lived publish tokens
- pin GitHub Actions to commit SHAs for high-risk workflows
- keep `pnpm-lock.yaml` committed

## References

- pnpm supply-chain guidance: <https://pnpm.io/supply-chain-security>
- pnpm workspace settings: <https://pnpm.io/settings>
- pnpm approve-builds: <https://pnpm.io/cli/approve-builds>
- CISA npm supply-chain alert: <https://www.cisa.gov/news-events/alerts/2025/09/23/widespread-supply-chain-compromise-impacting-npm-ecosystem>
- SANS Axios npm compromise write-up: <https://www.sans.org/blog/axios-npm-supply-chain-compromise-malicious-packages-remote-access-trojan>
