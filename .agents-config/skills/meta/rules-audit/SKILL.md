---
name: rules-audit
description: Run a deterministic, read-only audit of centralized rule cards, provider rule symlinks, path scopes, enforcement/wiki links, conflicts, and the AI workflow invocation framework. Use explicitly after changing .agents-config/rules or skill invocation policy.
disable-model-invocation: true
---

# Audit centralized rules

Run this read-only meta workflow when explicitly invoked or as a specialist step of an authorized development flow. From this skill directory:

```text
uv run scripts/audit_rules.py <repository-root>
uv run scripts/audit_rules.py <repository-root> --json
```

## Workflow

1. Capture the repository revision and dirty state.
2. Scan every configuration Markdown card in `.agents-config/rules/`.
3. Require metadata, matching `paths` and `applies_to`, unique IDs, real configuration/wiki targets, index coverage, and no direct required/prohibited contradiction.
4. Require `.agents/rules` and `.claude/rules` to be relative directory symlinks that resolve to `.agents-config/rules` and use Git mode `120000` when tracked.
5. Verify the skills rule covers the canonical typed tree and both flat project discovery roots.
6. Verify the global AI Workflow & Invocation Decision Framework remains intact:
   - type directories classify purpose but do not determine invocation mode;
   - `SKILL.md` and `agents/openai.yaml` are the provider-specific invocation authorities;
   - paired locks mark explicit-only skills, absent locks leave a skill contextual/model-eligible, and every skill remains directly user-invokable;
   - configuration, environment, destructive-Git, and issue-publication workflows retain explicit-only metadata and no provider-lock mismatch exists;
   - authorized development flows orchestrate specialists while actual action authority remains scoped to the approved task.
7. Report protected application paths with no matching non-global card, exact overlapping scopes, stale path spellings, and checks without real enforcement mappings.

The deterministic audit checks provider metadata and framework structure. Review prose for authorization boundaries; keyword matches cannot prove that a workflow preserves them.

Do not rewrite cards, repair symlinks, stage changes, or infer that an automated check exists. Propose the smallest correction and name the required human owner when scope or authority is unclear. Success requires zero errors and zero warnings.
