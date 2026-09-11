"""Check the real migration contracts; scheduler/network fixtures remain separate."""
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import workflow

class WorkflowContractPilot(unittest.TestCase):
    def test_repository_contracts_cover_approved_requirements(self):
        plan = workflow.validate_plan(ROOT, "specs/implementation-plans/2026-09-11-agent-development-workflow.md")
        self.assertEqual(plan["id"], "FEAT-AGENT-WORKFLOW")
        self.assertEqual(len(plan["stories"]), 6)
        self.assertEqual({r for s in plan["stories"] for r in s["requirements"]},
                         {f"REQ-{n:03}" for n in range(1, 10)})

if __name__ == "__main__":
    unittest.main()
