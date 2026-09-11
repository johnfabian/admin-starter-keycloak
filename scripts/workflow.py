# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Three-flow contracts and locked, revision-bound delivery state.

This is an evidence coordinator, not an authentication system or an agent harness.
The invoking agent must verify approval/reviewer provenance in the real session.
No arbitrary commands from Markdown or state are executed.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from uuid import uuid4

from runtime import ROOT, atomic_json, common_dir, exclusive_lock, executable, git, require_worktree

VERSION = 2
CHECKS = {"test:fast", "verify:story", "build", "graph:check"}
LAYERS = {"data", "service", "ui"}
SEVERITIES = {"critical", "high", "medium", "low"}
FINISHED = {"integrated"}
SHA = re.compile(r"[0-9a-f]{40}")
ID = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+")
FILENAME = re.compile(r"(\d{4}-\d{2}-\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md")
DENIED = {".git", ".agent-work", "node_modules", "graphify-out", ".venv", ".agents", ".claude", ".codex"}


class Invalid(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Invalid(message)


def digest_bytes(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def file_digest(path):
    return digest_bytes(Path(path).read_bytes())


def json_digest(data):
    return digest_bytes(json.dumps(data, sort_keys=True, separators=(",", ":")).encode())


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def nonempty(value):
    return isinstance(value, str) and bool(value.strip()) and not value.strip().upper().startswith(("TODO", "<"))


def strings(value):
    return isinstance(value, list) and bool(value) and all(nonempty(v) for v in value)


def safe_path(value):
    need(isinstance(value, str) and bool(value), "Path must be a nonempty string")
    need("\\" not in value and not any(c in value for c in "*?[]:\x00"), "Use normalized relative paths, not globs or aliases")
    parts = value.rstrip("/").split("/")
    need(all(p not in {"", ".", ".."} for p in parts), "Path traversal or empty component")
    need(not any(p.casefold() in DENIED or p.casefold().startswith(".env") for p in parts), "Excluded path in ownership")
    return "/".join(parts).casefold()


def overlap(a, b):
    a, b = safe_path(a), safe_path(b)
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def contains(budget, path):
    a, b = safe_path(budget), safe_path(path)
    return b == a or b.startswith(a + "/")


def inside(root, relative):
    need(not Path(relative).is_absolute(), "Artifact path must be repository-relative")
    p = root / relative
    need(p.resolve().is_relative_to(root.resolve()), "Artifact escapes repository")
    need(not any(x.is_symlink() for x in [p, *p.parents] if x != root.parent), "Artifact path cannot traverse symlinks")
    return p


def read_contract(root, relative, kind):
    need(kind in {"feature-spec", "implementation-plan"}, "Unknown contract kind")
    folder = "features" if kind == "feature-spec" else "implementation-plans"
    p = inside(root, relative)
    need(p.parent == root / "specs" / folder, f"Place {kind} in specs/{folder}/")
    match = FILENAME.fullmatch(p.name)
    need(match, "Use YYYY-MM-DD-feature-slug.md")
    try:
        date.fromisoformat(match[1])
    except ValueError as exc:
        raise Invalid("Invalid artifact date") from exc
    text = p.read_text(encoding="utf-8")
    fence = chr(96) * 3
    blocks = re.findall(fence + kind + r"\s*\n(.*?)\n" + fence, text, re.S)
    need(len(blocks) == 1, f"Expected exactly one {kind} JSON block")
    try:
        result = json.loads(blocks[0])
    except (ValueError, TypeError) as exc:
        raise Invalid(f"Invalid {kind} JSON") from exc
    need(isinstance(result, dict) and result.get("version") == VERSION, "Unsupported contract version")
    need(ID.fullmatch(str(result.get("id", ""))), "Invalid stable feature ID")
    need(nonempty(result.get("title")), "Missing feature title")
    return result


def validate_spec(root, relative):
    data = read_contract(root, relative, "feature-spec")
    need(strings(data.get("scope")) and strings(data.get("nonGoals")), "Specification needs scope and nonGoals")
    requirements = data.get("requirements")
    need(isinstance(requirements, list) and requirements, "Specification needs requirements")
    ids = set()
    for req in requirements:
        need(isinstance(req, dict), "Requirement must be an object")
        rid = req.get("id", "")
        need(re.fullmatch(r"REQ-\d{3,}", str(rid)) and rid not in ids, "Invalid/duplicate requirement ID")
        ids.add(rid)
        need(all(nonempty(req.get(k)) for k in ("actor", "outcome", "denied", "failure")), f"{rid}: incomplete behavior")
        need(strings(req.get("acceptance")), f"{rid}: acceptance evidence missing")
    decisions = data.get("decisions", [])
    need(isinstance(decisions, list), "decisions must be an array")
    for item in decisions:
        need(isinstance(item, dict) and nonempty(item.get("question")), "Invalid decision")
        need(item.get("status") in {"resolved", "deferred"}, "Resolve material pending decisions before planning approval")
        need(nonempty(item.get("disposition")), "Decision needs explicit disposition")
    return data


def validate_plan(root, relative):
    plan = read_contract(root, relative, "implementation-plan")
    spec_path = plan.get("specification", "")
    spec = validate_spec(root, spec_path)
    need(plan["id"] == spec["id"], "Feature IDs differ")
    need(plan.get("specificationDigest") == file_digest(root / spec_path), "Specification changed; revise and critique the plan")
    required = {r["id"] for r in spec["requirements"]}
    stories = plan.get("stories")
    need(isinstance(stories, list) and stories, "Plan needs at least one vertical story")
    shared = plan.get("integrationPaths", [])
    need(isinstance(shared, list), "integrationPaths must be an array")
    for path in shared:
        safe_path(path)
    by_id = {}
    covered = set()
    for story in stories:
        need(isinstance(story, dict), "Story must be an object")
        sid = story.get("id", "")
        need(re.fullmatch(r"STORY-\d{3,}", str(sid)) and sid not in by_id, "Invalid/duplicate story ID")
        by_id[sid] = story
        need(all(nonempty(story.get(k)) for k in ("title", "outcome", "rollback")), f"{sid}: missing outcome/rollback")
        need(strings(story.get("requirements")), f"{sid}: missing requirement mapping")
        need(set(story["requirements"]) <= required, f"{sid}: unknown requirements")
        covered.update(story["requirements"])
        need(strings(story.get("acceptance")) and strings(story.get("tests")), f"{sid}: missing acceptance/tests")
        need(strings(story.get("verification")) and set(story["verification"]) <= CHECKS, f"{sid}: unsupported verification command")
        need(strings(story.get("ownedPaths")), f"{sid}: no path ownership")
        for path in story["ownedPaths"]:
            safe_path(path)
            need(not any(overlap(path, p) for p in shared), f"{sid}: shared integration path belongs to integration owner")
        layers = story.get("layers", {})
        need(isinstance(layers, dict) and set(layers) == LAYERS, f"{sid}: explain data/service/ui applicability")
        need(all(nonempty(x) for x in layers.values()), f"{sid}: layer must describe work or explain why not applicable")
        need(story.get("kind") in {"vertical", "enabling"}, f"{sid}: invalid kind")
        if story["kind"] == "enabling":
            need(nonempty(story.get("justification")), f"{sid}: enabling work needs justification")
        deps = story.get("dependsOn")
        need(isinstance(deps, list) and all(isinstance(d, str) for d in deps), f"{sid}: dependencies must be an array")
        need(len(deps) == len(set(deps)), f"{sid}: duplicate dependency")
    need(covered == required, "Plan leaves requirements uncovered")
    ancestors = {}
    def visit(sid, stack):
        need(sid in by_id, f"Unknown dependency: {sid}")
        need(sid not in stack, "Dependency cycle")
        if sid in ancestors:
            return ancestors[sid]
        result = set()
        for dep in by_id[sid]["dependsOn"]:
            result.add(dep)
            result.update(visit(dep, stack | {sid}))
        ancestors[sid] = result
        return result
    for sid in by_id:
        visit(sid, set())
    for left, a in by_id.items():
        for right, b in by_id.items():
            if left >= right or left in ancestors[right] or right in ancestors[left]:
                continue
            need(not any(overlap(x, y) for x in a["ownedPaths"] for y in b["ownedPaths"]),
                 f"{left}/{right}: unordered path ownership overlap; add a dependency or split ownership")
    return plan


def identity(root):
    root = Path(root).resolve()
    branch = require_worktree(root)
    return {"root": str(root), "branch": branch, "common": str(common_dir(root).resolve()),
            "head": git("rev-parse", "HEAD", root=root)}


def clean(root):
    need(not git("status", "--porcelain", root=root), "Commit or preserve unrelated changes before this operation")


def ancestor(old, new, root):
    return subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", old, new],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def repo_slug(url):
    match = re.fullmatch(r"(?:https://github\.com/|git@github\.com:)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?", url)
    need(match, "Only explicit GitHub origin URLs are supported for publication")
    return match[1]


def push_destination(root, repository):
    urls = git("remote", "get-url", "--push", "--all", "origin", root=root).splitlines()
    need(len(urls) == 1 and repo_slug(urls[0]) == repository, "Effective push destination differs from approval")
    return urls[0]


def report(root, path, expected):
    p = Path(path).resolve()
    need(p.is_relative_to(root.resolve()) and not p.is_symlink(), "Evidence must be a local regular file in the integration worktree")
    data = json.loads(p.read_text(encoding="utf-8"))
    need(isinstance(data, dict), "Evidence must be an object")
    for key, value in expected.items():
        need(data.get(key) == value, f"Evidence mismatch: {key}")
    return {"path": str(p), "digest": file_digest(p), "data": data}


def verify_report(record):
    need(file_digest(record["path"]) == record["digest"], "Recorded evidence changed")
    need(json.loads(Path(record["path"]).read_text(encoding="utf-8")) == record["data"], "Cached evidence differs from source")


class Workflow:
    def __init__(self, root, state):
        self.root = Path(root).resolve()
        self.location = identity(self.root)
        self.state_path = Path(state)
        if not self.state_path.is_absolute():
            self.state_path = self.root / self.state_path
        self.state_path = self.state_path.resolve()
        need(self.state_path.is_relative_to(self.root / ".agent-work"), "State belongs under integration worktree .agent-work/")
        self.common = common_dir(self.root) / "agent-workflow"
        self.registry_path = self.common / "claims.json"
        self.lock_path = self.common / "coordination.lock"

    def save(self, state, registry):
        state["generation"] += 1
        state["updatedAt"] = now()
        # Registry first: a crash may retain ownership, but must never free it silently.
        atomic_json(self.registry_path, registry)
        atomic_json(self.state_path, state)

    def load(self):
        self.location = identity(self.root)
        data = json.loads(self.state_path.read_text(encoding="utf-8"))
        need(data.get("version") == VERSION, "Legacy state cannot authorize v2 work; reinitialize from reviewed artifacts")
        need(data.get("root") == str(self.root) and data.get("branch") == self.location["branch"], "Wrong integration worktree/branch")
        spec = validate_spec(self.root, data["specification"])
        plan = validate_plan(self.root, data["plan"])
        need(spec["id"] == data["featureId"] == plan["id"], "Feature identity changed")
        need(file_digest(self.root / data["specification"]) == data["specDigest"], "Approved specification changed")
        need(file_digest(self.root / data["plan"]) == data["planDigest"], "Approved implementation plan changed")
        need(ancestor(data["baseRevision"], self.location["head"], self.root), "Integration branch lost its base")
        need(set(data["stories"]) == {x["id"] for x in plan["stories"]}, "Story set changed")
        need(isinstance(data["round"], int) and 1 <= data["round"] <= 5, "Invalid review round")
        for sid, item in data["stories"].items():
            need(item["status"] in {"pending", "active", "verified", "blocked", "integrated"}, "Invalid story status")
            if item["status"] == "integrated":
                need(ancestor(item["revision"], self.location["head"], self.root), "Integrated prerequisite is not in current HEAD")
                story = next(x for x in plan["stories"] if x["id"] == sid)
                self.verified(item.get("verification"), item["revision"], story["verification"])
                need(ancestor(item["integratedAt"], self.location["head"], self.root), "Integrated verification revision lost")
                self.verified(item.get("integrationVerification"), item["integratedAt"], story["verification"])
                need(isinstance(item.get("resolutionRequired"), bool), "Missing integration resolution disposition")
                if item["resolutionRequired"]:
                    resolved = item.get("resolutionReview")
                    need(resolved and resolved.get("passed"), "Missing passing resolution review")
                    verify_report(resolved)
                    need(resolved["data"].get("kind") == "implementation" and
                         resolved["data"].get("subject") == "integration:" + sid and
                         resolved["data"].get("revision") == item["integratedAt"], "Resolution review changed")
                    self.findings(resolved["data"])
                review = item.get("review")
                need(review and review.get("passed"), "Integrated story lacks passing review")
                verify_report(review)
                need(review["data"].get("revision") == item["revision"] and review["data"].get("subject") == sid, "Integrated review changed")
                self.findings(review["data"])
        return data, plan

    @contextmanager
    def transaction(self, generation=None):
        with exclusive_lock(self.lock_path, "Feature coordination"):
            state, plan = self.load()
            if generation is not None:
                need(state["generation"] == generation, "Stale generation; reread status")
            registry = json.loads(self.registry_path.read_text()) if self.registry_path.exists() else {}
            yield state, plan, registry
            self.save(state, registry)

    def initialize(self, specification, plan_path, capabilities):
        with exclusive_lock(self.lock_path, "Feature coordination"):
            need(not self.state_path.exists(), "State exists; resume it instead of resetting counters")
            clean(self.root)
            spec = validate_spec(self.root, specification)
            plan = validate_plan(self.root, plan_path)
            need(capabilities.get("independentReview") is True, "Independent reviewer capability required")
            need(capabilities.get("worktrees") is True, "Linked worktree capability required")
            need(isinstance(capabilities.get("parallel"), bool), "Declare parallel capability")
            need(nonempty(capabilities.get("harness")), "Declare the actual harness")
            need(nonempty(capabilities.get("coordinator")), "Identify the actual integration writer")
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            state = {"version": VERSION, "generation": 0, "root": str(self.root), "branch": self.location["branch"],
                     "featureId": spec["id"], "specification": specification, "plan": plan_path,
                     "specDigest": file_digest(self.root / specification), "planDigest": file_digest(self.root / plan_path),
                     "baseRevision": self.location["head"], "capabilities": capabilities, "approval": None,
                     "planningReviews": {}, "round": 1, "roundHistory": [], "finalReview": None,
                     "finalVerification": None, "publication": None,
                     "stories": {s["id"]: {"status": "pending"} for s in plan["stories"]}}
            atomic_json(self.state_path, state)
            return state

    def record_planning_review(self, kind, path, generation):
        need(kind in {"spec", "plan"}, "Review kind must be spec or plan")
        with self.transaction(generation) as (s, p, r):
            need(s["approval"] is None, "Planning approval is immutable; initialize a new reviewed plan if scope changes")
            evidence = report(self.root, path, {"kind": kind, "specDigest": s["specDigest"],
                                                "planDigest": s["planDigest"]})
            d = evidence["data"]
            need(nonempty(d.get("author")) and nonempty(d.get("reviewer")) and d["author"] != d["reviewer"],
                 "Planning critique must identify a separate author and reviewer")
            try:
                self.findings(d)
                evidence["passed"] = True
            except Invalid:
                evidence["passed"] = False
            s["planningReviews"][kind] = evidence
            return {"passed": evidence["passed"]}

    @staticmethod
    def findings(data):
        need(isinstance(data.get("findings"), list), "Review needs explicit findings array")
        for item in data["findings"]:
            need(isinstance(item, dict) and item.get("severity") in SEVERITIES and nonempty(item.get("evidence")),
                 "Invalid review finding")
            need(item.get("disposition") in {"open", "fixed", "accepted"}, "Invalid finding disposition")
            need(not (item["severity"] in {"critical", "high"} and item["disposition"] != "fixed"),
                 "Unresolved blocking finding; no automatic risk acceptance")

    def approve(self, path, generation):
        with self.transaction(generation) as (s, p, r):
            need(s["approval"] is None, "Approval cannot be overwritten")
            need(set(s["planningReviews"]) == {"spec", "plan"}, "Both independent planning critiques are required")
            for review in s["planningReviews"].values():
                verify_report(review)
                need(review.get("passed"), "Planning critique has blocking findings")
                self.findings(review["data"])
            evidence = report(self.root, path, {"specDigest": s["specDigest"], "planDigest": s["planDigest"]})
            a = evidence["data"]
            need(nonempty(a.get("actor")) and a["actor"].startswith("human:"), "Approval must identify a human")
            need(nonempty(a.get("statement")) and a.get("sourceKind") in {"conversation", "github"},
                 "Actual human instruction and provenance are required; state fields do not grant authority")
            need(nonempty(a.get("source")) and nonempty(a.get("approvedAt")), "Missing attributable approval source/time")
            try:
                datetime.fromisoformat(a["approvedAt"].replace("Z", "+00:00"))
            except ValueError as exc:
                raise Invalid("Approval timestamp is invalid") from exc
            target = a.get("target", {})
            expected_repo = repo_slug(git("remote", "get-url", "origin", root=self.root))
            need(target.get("repository") == expected_repo and target.get("branch") == s["branch"], "Approval destination differs")
            need(nonempty(target.get("base")) and not target["base"].startswith("-"), "Missing target base")
            need(set(a.get("actions", [])) == {"implement", "commit", "push", "pull-request"},
                 "Approve explicit delivery scope through PR submission")
            push_destination(self.root, expected_repo)
            s["approval"] = evidence

    def authority(self, s):
        need(s["approval"] is not None, "Implementation requires actual human approval")
        verify_report(s["approval"])
        target = s["approval"]["data"]["target"]
        push_destination(self.root, target["repository"])
        need(repo_slug(git("remote", "get-url", "origin", root=self.root)) == target["repository"],
             "Origin changed since approval")
        for evidence in s["planningReviews"].values():
            verify_report(evidence)

    def ready(self, s, p, registry):
        active = list(registry.values())
        capacity = (2 if s["capabilities"]["parallel"] else 1) - len(active)
        candidates = []
        for story in p["stories"]:
            if capacity <= 0:
                break
            if s["stories"][story["id"]]["status"] != "pending":
                continue
            if not all(s["stories"][d]["status"] == "integrated" for d in story["dependsOn"]):
                continue
            if any(overlap(x, y) for claim in active for x in story["ownedPaths"] for y in claim["paths"]):
                continue
            candidates.append(story["id"])
            active.append({"paths": story["ownedPaths"]})
            capacity -= 1
        return candidates

    def status(self):
        with exclusive_lock(self.lock_path, "Feature coordination"):
            s, p = self.load()
            registry = json.loads(self.registry_path.read_text()) if self.registry_path.exists() else {}
            if s["approval"]:
                self.authority(s)
            return {"generation": s["generation"], "round": s["round"], "approved": bool(s["approval"]),
                    "ready": self.ready(s, p, registry) if s["approval"] else [],
                    "stories": s["stories"], "claims": registry, "publication": s["publication"]}

    def claim_key(self, story):
        return str(self.state_path).casefold() + ":" + story

    def claim(self, sid, worktree, agent, generation):
        with self.transaction(generation) as (s, p, registry):
            self.authority(s)
            need(sid in self.ready(s, p, registry), "Story is blocked, owned, not dependency-ready, or capacity is exhausted")
            loc = identity(Path(worktree))
            need(loc["common"] == self.location["common"] and loc["root"] != str(self.root), "Use a dedicated linked writer worktree")
            need(loc["head"] == self.location["head"], "Worker must start at the current integration HEAD")
            need(nonempty(agent), "Identify the writing agent")
            need(not any(c["worktree"].casefold() == loc["root"].casefold() or c["branch"] == loc["branch"]
                         for c in registry.values()), "Worker branch/worktree already reserved")
            clean(Path(loc["root"]))
            story = next(x for x in p["stories"] if x["id"] == sid)
            for owned in story["ownedPaths"]:
                inside(Path(loc["root"]), owned)
            key = self.claim_key(sid)
            registry[key] = {"worktree": loc["root"], "branch": loc["branch"], "agent": agent,
                             "paths": story["ownedPaths"], "state": str(self.state_path), "story": sid}
            s["stories"][sid] = {"status": "active", "agent": agent, "worktree": loc["root"],
                                 "branch": loc["branch"], "baseRevision": loc["head"],
                                 "verification": None, "review": None}
            return {"story": story, "integrationRoot": str(self.root), "state": str(self.state_path),
                    "worktree": loc["root"], "branch": loc["branch"], "baseRevision": loc["head"],
                    "specDigest": s["specDigest"], "planDigest": s["planDigest"],
                    "instructions": "Run agent:setup/check before edits. Use implement-story. Commit only owned changes; coordinate shared files. Never self-review."}

    def worker(self, s, p, sid):
        need(sid in s["stories"], "Unknown story")
        item = s["stories"][sid]
        need(item["status"] in {"active", "verified", "blocked"}, "Story has no active worker")
        root = Path(item["worktree"])
        loc = identity(root)
        need(loc["common"] == self.location["common"] and loc["branch"] == item["branch"], "Worker identity changed")
        clean(root)
        need(ancestor(item["baseRevision"], loc["head"], root), "Worker lost its assigned base")
        story = next(x for x in p["stories"] if x["id"] == sid)
        changed = git("diff", "--name-only", "--no-renames", item["baseRevision"], loc["head"], root=root).splitlines()
        need(changed, "Story contains no committed changes")
        for name in changed:
            need(any(contains(b, name) for b in story["ownedPaths"]), f"Out-of-scope worker path: {name}")
            # Ownership never permits a file to redirect access outside the worktree.
            inside(root, name)
        return item, story, loc

    def run_checks(self, root, checks, label):
        head = git("rev-parse", "HEAD", root=root)
        records = []
        for check in checks:
            need(check in CHECKS, "Unsupported check")
            path = self.state_path.parent / (label + "-" + check.replace(":", "-") + "-" + uuid4().hex + ".log")
            with path.open("w", encoding="utf-8") as stream:
                result = subprocess.run([executable("corepack"), "pnpm", check], cwd=root,
                                        stdout=stream, stderr=subprocess.STDOUT, text=True)
            records.append({"command": check, "exitCode": result.returncode, "log": str(path),
                            "logDigest": file_digest(path), "revision": head, "at": now()})
            if result.returncode:
                raise Invalid(f"Verification failed: {check}; inspect the ignored local log")
        clean(root)
        need(git("rev-parse", "HEAD", root=root) == head, "Revision changed while verifying")
        return {"revision": head, "checks": records}

    @staticmethod
    def verified(evidence, head, required=None):
        need(isinstance(evidence, dict) and evidence.get("revision") == head, "Missing/stale verification")
        need(bool(evidence.get("checks")), "Missing command evidence")
        if required is not None:
            need({x.get("command") for x in evidence["checks"]} == set(required), "Required command evidence missing")
        for check in evidence["checks"]:
            need(check["exitCode"] == 0 and check["revision"] == head, "Failed/stale verification")
            need(file_digest(check["log"]) == check["logDigest"], "Verification evidence changed")

    def verify_story(self, sid, generation):
        with self.transaction(generation) as (s, p, r):
            self.authority(s)
            item, story, loc = self.worker(s, p, sid)
            item["verification"] = None
            item["review"] = None
            item["status"] = "blocked"
            self.save(s, r)  # Persist invalidation before execution, including process interruption.
            try:
                item["verification"] = self.run_checks(Path(loc["root"]), story["verification"], sid)
                item["status"] = "verified"
                failure = None
            except (Invalid, OSError, RuntimeError, subprocess.CalledProcessError) as exc:
                item["status"] = "blocked"
                failure = str(exc)
        if failure:
            raise Invalid(failure)

    def review(self, sid, path, generation):
        with self.transaction(generation) as (s, p, r):
            self.authority(s)
            if sid == "feature":
                clean(self.root)
                need(all(x["status"] == "integrated" for x in s["stories"].values()), "Integrate all stories before final review")
                head = self.location["head"]
                self.verified(s["finalVerification"], head, ["verify:story"])
                writers = {x["agent"] for x in s["stories"].values()} | {s["capabilities"]["coordinator"]}
            else:
                item, story, loc = self.worker(s, p, sid)
                head = loc["head"]
                self.verified(item["verification"], head, story["verification"])
                writers = {item["agent"], s["capabilities"]["coordinator"]}
            evidence = report(self.root, path, {"kind": "implementation", "subject": sid, "revision": head, "round": s["round"]})
            d = evidence["data"]
            need(nonempty(d.get("reviewer")) and d["reviewer"] not in writers, "Reviewer must be independent of the writer")
            previous = [e for e in s["roundHistory"] if e["data"]["round"] == s["round"] and e["data"]["subject"] == sid]
            if previous:
                need(previous[0]["digest"] == evidence["digest"], "Subject already reviewed this round; advance the shared feature round")
                verify_report(previous[0])
                if sid == "feature":
                    s["finalReview"] = previous[0]
                else:
                    item["review"] = previous[0]
                    item["status"] = "verified" if previous[0]["passed"] else "blocked"
                return {"passed": previous[0]["passed"], "round": s["round"], "exhausted": not previous[0]["passed"] and s["round"] == 5}
            # Store failed reviews too: never erase finding history to reset the budget.
            need(isinstance(d.get("findings"), list), "Review needs findings")
            s["roundHistory"].append(evidence)
            try:
                self.findings(d)
                passed = True
            except Invalid:
                passed = False
            evidence["passed"] = passed
            if sid == "feature":
                s["finalReview"] = evidence
            else:
                item["review"] = evidence
                item["status"] = "verified" if passed else "blocked"
            return {"passed": passed, "round": s["round"], "exhausted": not passed and s["round"] == 5}

    def next_round(self, reason, generation):
        with self.transaction(generation) as (s, p, r):
            self.authority(s)
            need(nonempty(reason), "Record why another feature review round is needed")
            need(s["round"] < 5, "Five review rounds exhausted; stop and escalate unresolved findings")
            need(any(e["data"]["round"] == s["round"] for e in s["roundHistory"]), "Review current round before advancing")
            s["round"] += 1
            s["finalReview"] = None
            for item in s["stories"].values():
                if item["status"] == "blocked":
                    item["status"] = "active"
                    item["review"] = None
                    item["verification"] = None

    def integrate(self, sid, generation, resolution_review=None):
        with self.transaction(generation) as (s, p, registry):
            self.authority(s)
            clean(self.root)
            item, story, loc = self.worker(s, p, sid)
            self.verified(item["verification"], loc["head"], story["verification"])
            review = item["review"]
            need(review and review.get("passed") and review["data"]["revision"] == loc["head"], "Independent passing review required")
            verify_report(review)
            need(all(s["stories"][d]["status"] == "integrated" for d in story["dependsOn"]), "Prerequisite not integrated")
            recovered = ancestor(loc["head"], self.location["head"], self.root)
            if not recovered:
                subprocess.run(["git", "-C", str(self.root), "merge", "--no-ff", "--no-edit", loc["head"]], check=True)
            new_head = git("rev-parse", "HEAD", root=self.root)
            # Do not release dependents on worker-only evidence. A failed merge check
            # retains the claim, and recovery requires review of the resolved candidate.
            integrated_checks = self.run_checks(self.root, story["verification"], "integration-" + sid)
            if recovered:
                need(resolution_review, "Recovered/resolved integration requires independent resolution review")
                resolved = report(self.root, resolution_review, {"kind": "implementation",
                                  "subject": "integration:" + sid, "revision": new_head, "round": s["round"]})
                need(nonempty(resolved["data"].get("reviewer")) and
                     resolved["data"]["reviewer"] not in {item["agent"], s["capabilities"]["coordinator"]},
                     "Resolution reviewer must be independent")
                prior = [e for e in s["roundHistory"] if e["data"]["round"] == s["round"] and
                         e["data"]["subject"] == "integration:" + sid]
                if prior:
                    need(prior[0]["digest"] == resolved["digest"], "Resolution already reviewed this round")
                    verify_report(prior[0])
                else:
                    try:
                        self.findings(resolved["data"])
                        resolved["passed"] = True
                    except Invalid:
                        resolved["passed"] = False
                    s["roundHistory"].append(resolved)
                    self.save(s, registry)
                need((prior[0] if prior else resolved).get("passed"), "Resolution has blocking review findings")
                item["resolutionReview"] = prior[0] if prior else resolved
            item.update(status="integrated", revision=loc["head"], integratedAt=new_head,
                        integrationVerification=integrated_checks, resolutionRequired=recovered)
            registry.pop(self.claim_key(sid), None)
            s["finalVerification"] = s["finalReview"] = None

    def release(self, sid, reason, reconciled, generation):
        with self.transaction(generation) as (s, p, registry):
            self.authority(s)
            need(reconciled and nonempty(reason), "Confirm the actual worker has stopped and record reconciliation")
            item = s["stories"][sid]
            need(item["status"] in {"active", "blocked", "verified"}, "No worker to release")
            clean(Path(item["worktree"]))
            # Preserve branch/commits and record the abandoned owner. Never kill/reset it.
            s.setdefault("released", []).append({**item, "reason": reason, "at": now()})
            s["stories"][sid] = {"status": "pending"}
            registry.pop(self.claim_key(sid), None)

    def verify_feature(self, generation):
        with self.transaction(generation) as (s, p, registry):
            self.authority(s)
            need(all(x["status"] == "integrated" for x in s["stories"].values()), "All stories must be integrated")
            need(not any(c["state"] == str(self.state_path) for c in registry.values()), "Active worker claim remains")
            clean(self.root)
            s["finalVerification"] = None
            s["finalReview"] = None
            self.save(s, registry)  # A killed check must not leave earlier passing evidence usable.
            try:
                s["finalVerification"] = self.run_checks(self.root, ["verify:story"], "feature")
                failure = None
            except (Invalid, OSError, RuntimeError, subprocess.CalledProcessError) as exc:
                failure = str(exc)
        if failure:
            raise Invalid(failure)

    def publish(self, title, body_path, generation):
        with self.transaction(generation) as (s, p, registry):
            self.authority(s)
            clean(self.root)
            head = self.location["head"]
            need(all(x["status"] == "integrated" for x in s["stories"].values()), "Unfinished stories")
            self.verified(s["finalVerification"], head, ["verify:story"])
            rev = s["finalReview"]
            need(rev and rev.get("passed") and rev["data"]["revision"] == head, "Final independent review does not match HEAD")
            verify_report(rev)
            need(nonempty(title) and not title.startswith("-"), "PR title required")
            body_file = Path(body_path).resolve()
            need(body_file.is_relative_to(self.root / ".agent-work"), "Prepare publication body under .agent-work/")
            body = body_file.read_text(encoding="utf-8")
            marker = "<!-- feature-workflow: " + s["featureId"] + " -->"
            need(marker in body and head in body, "PR body needs the stable feature marker and verified revision")
            target = s["approval"]["data"]["target"]
            def gh(*args):
                return subprocess.check_output([executable("gh"), *args], cwd=self.root, text=True, encoding="utf-8")
            matches = json.loads(gh("pr", "list", "--repo", target["repository"], "--head", target["branch"], "--state", "open",
                                   "--json", "number,headRefName,headRefOid,baseRefName,body,url,title,isCrossRepository,headRepository,headRepositoryOwner"))
            need(len(matches) <= 1, "Duplicate PR candidates")
            existing = matches[0] if matches else None
            def same_repository(candidate):
                return (candidate.get("isCrossRepository") is False and
                        (candidate.get("headRepositoryOwner") or {}).get("login", "") + "/" +
                        (candidate.get("headRepository") or {}).get("name", "") == target["repository"])
            if existing:
                need(same_repository(existing), "Existing PR head repository differs")
                need(existing["baseRefName"] == target["base"] and existing["headRefName"] == target["branch"], "Existing PR target conflicts")
                need(marker in existing["body"], "Existing PR belongs to a different workflow")
                prior = s.get("publication") or {}
                need(existing["body"] == body or digest_bytes(existing["body"].encode()) == prior.get("bodyDigest"),
                     "Existing PR body conflicts; reconcile edits before publication")
                allowed_head = s.get("publication", {}).get("revision") if s.get("publication") else head
                need(existing["headRefOid"] in {head, allowed_head}, "Existing PR head conflicts")
            # Validate remote branch before push; never force-push or overwrite divergence.
            remote = git("ls-remote", "origin", "refs/heads/" + s["branch"], root=self.root).split()
            if remote:
                need(ancestor(remote[0], head, self.root), "Remote branch diverged; reconcile before publication")
            need(git("rev-parse", "HEAD", root=self.root) == head, "Candidate changed before push")
            destination = push_destination(self.root, target["repository"])
            subprocess.run(["git", "-C", str(self.root), "push", destination, s["branch"] + ":refs/heads/" + s["branch"]], check=True)
            need(git("rev-parse", "HEAD", root=self.root) == head, "Candidate changed during publication")
            if existing:
                gh("pr", "edit", str(existing["number"]), "--repo", target["repository"], "--title", title, "--body-file", str(body_file))
                number = str(existing["number"])
            else:
                url = gh("pr", "create", "--repo", target["repository"], "--base", target["base"], "--head", s["branch"],
                         "--title", title, "--body-file", str(body_file)).strip()
                number = url.rsplit("/", 1)[-1]
            actual = json.loads(gh("pr", "view", number, "--repo", target["repository"], "--json", "url,body,title,headRefOid,baseRefName,isCrossRepository,headRepository,headRepositoryOwner"))
            need(same_repository(actual) and actual["body"] == body and actual["title"] == title and actual["headRefOid"] == head and actual["baseRefName"] == target["base"],
                 "PR read-back differs; retain checkpoint and reconcile before retry")
            s["publication"] = {"url": actual["url"], "revision": head, "bodyDigest": file_digest(body_file), "verifiedAt": now()}
            return s["publication"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--state", default=".agent-work/feature/state.json")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("check-spec", "check-plan"):
        sub.add_parser(command).add_argument("path")
    init = sub.add_parser("init")
    init.add_argument("--spec", required=True)
    init.add_argument("--plan", required=True)
    init.add_argument("--capabilities", required=True)
    sub.add_parser("status")
    for command in ("planning-review", "approve", "claim", "verify-story", "review", "next-round", "integrate", "release", "verify-feature", "publish"):
        cmd = sub.add_parser(command)
        cmd.add_argument("--generation", type=int, required=True)
        if command in {"claim", "verify-story", "review", "integrate", "release"}:
            cmd.add_argument("--story", required=True)
        if command in {"planning-review", "approve", "review"}:
            cmd.add_argument("--record", required=True)
        if command == "planning-review":
            cmd.add_argument("--kind", choices=["spec", "plan"], required=True)
        if command == "claim":
            cmd.add_argument("--worktree", required=True)
            cmd.add_argument("--agent", required=True)
        if command in {"release", "next-round"}:
            cmd.add_argument("--reason", required=True)
        if command == "release":
            cmd.add_argument("--reconciled", action="store_true")
        if command == "integrate":
            cmd.add_argument("--resolution-review")
        if command == "publish":
            cmd.add_argument("--title", required=True)
            cmd.add_argument("--body-file", required=True)
    args = parser.parse_args([x for x in sys.argv[1:] if x != "--"])
    root = args.root.resolve()
    if args.command.startswith("check-"):
        result = (validate_spec if args.command == "check-spec" else validate_plan)(root, args.path)
        print(json.dumps({"valid": True, "feature": result["id"]}))
        return
    flow = Workflow(root, args.state)
    commands = {
        "init": lambda: flow.initialize(args.spec, args.plan, json.loads(Path(args.capabilities).read_text())),
        "status": flow.status,
        "planning-review": lambda: flow.record_planning_review(args.kind, args.record, args.generation),
        "approve": lambda: flow.approve(args.record, args.generation),
        "claim": lambda: flow.claim(args.story, args.worktree, args.agent, args.generation),
        "verify-story": lambda: flow.verify_story(args.story, args.generation),
        "review": lambda: flow.review(args.story, args.record, args.generation),
        "next-round": lambda: flow.next_round(args.reason, args.generation),
        "integrate": lambda: flow.integrate(args.story, args.generation, args.resolution_review),
        "release": lambda: flow.release(args.story, args.reason, args.reconciled, args.generation),
        "verify-feature": lambda: flow.verify_feature(args.generation),
        "publish": lambda: flow.publish(args.title, args.body_file, args.generation),
    }
    result = commands[args.command]()
    print(json.dumps(result if result is not None else flow.status(), indent=2))


if __name__ == "__main__":
    try:
        main()
    except (Invalid, OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"Workflow stopped: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
