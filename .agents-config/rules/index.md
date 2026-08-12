# Scoped rule catalog

Match proposed changed or reviewed paths against this table. Load `global` plus only the matching cards.

| Rule                            | Applies to                                                                                              | Automated enforcement                                    |
| ------------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| [global](global.md)             | Every repository path                                                                                   | Prettier; repository `check` where applicable            |
| [react-router](react-router.md) | Implemented React Router app and its TypeScript/build configuration under `web/`                        | ESLint, React Router type generation, TypeScript, build  |
| [express](express.md)           | `api-express/`, currently a documented placeholder                                                      | Prettier only; Express checks do not yet exist           |
| [testing](testing.md)           | Test files/directories and test-runner configuration                                                    | No test runner currently declared                        |
| [security](security.md)         | Auth/session, identity, proxy, database, backup/restore, Docker, environment, and dependency boundaries | Static app gate plus applicable configuration review     |
| [skills](skills.md)             | Typed shared skill packages, provider discovery symlinks, and the README skill catalog                  | Skills audit, package/catalog validation, symlink review |

Overlapping cards are cumulative. If directives conflict, stop and request owner direction; do not choose silently.
