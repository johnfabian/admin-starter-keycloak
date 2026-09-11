import type { Reporter, TestCase, TestResult, FullResult } from "@playwright/test/reporter";
import { writeFileSync, rmSync } from "node:fs";
import { join, relative, resolve } from "node:path";
export default class SafeReporter implements Reporter {
  private results: { title: string; status: string; duration: number; failures?: string[] }[] = [];
  onTestEnd(test: TestCase, result: TestResult) {
    // No raw exception, DOM, URL, request, cookie, password, or stdout attachments.
    const root = process.env.PW_RUN_DIR ? resolve(process.env.PW_RUN_DIR, "results") : undefined;
    for (const attachment of result.attachments) {
      if (root && attachment.name === "error-context" && attachment.path) {
        const within = relative(root, resolve(attachment.path));
        if (within && !within.startsWith("..") && !within.includes(":"))
          rmSync(attachment.path, { force: true });
      }
    }
    const entry = {
      title: test.titlePath().slice(1).join(" > "),
      status: result.status,
      duration: result.duration,
      failures: result.errors.map((error) => {
        const stack = error.stack || "";
        const location =
          stack.match(/(?:auth|ui|registration)\.spec\.ts:\d+:\d+/)?.[0] || "setup or fixture";
        const plain = (error.message || "").replace(/\x1b\[[0-9;]*m/g, "");
        const status = plain.match(
          /Expected: ([1-5]\d{2})(?!\d)[\s\S]*Received: ([1-5]\d{2})(?!\d)/
        );
        return (
          location +
          (status
            ? " expected number " + status[1] + ", received " + status[2]
            : /timeout/i.test(plain)
              ? " timeout"
              : " assertion or setup failure")
        );
      }),
    };
    this.results.push(entry);
    console.log(
      entry.status +
        ": " +
        entry.title +
        (entry.failures.length ? " [" + entry.failures.join("; ") + "]" : "")
    );
  }
  onEnd(result: FullResult) {
    const report = { status: result.status, tests: this.results };
    if (process.env.PW_RUN_DIR)
      writeFileSync(join(process.env.PW_RUN_DIR, "summary.json"), JSON.stringify(report, null, 2));
    console.log("Browser result: " + result.status);
  }
}
