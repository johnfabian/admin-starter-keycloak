import { test as base, expect, type Page } from "@playwright/test";
import { readFileSync, mkdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";
export const root = path.resolve(fileURLToPath(new URL("../..", import.meta.url)));
export const routes = (await import("../../web/app/lib/app-settings.shared")).appRoutes;
export interface Account {
  id?: string;
  username: string;
  email: string;
  password: string;
  role: string;
}
export interface Fixtures {
  runId: string;
  users: Record<string, Account>;
  registration: Account;
}
export function fixtures(): Fixtures {
  const location = process.env.PW_FIXTURE_MANIFEST;
  if (!location)
    throw new Error("Use the root test:e2e runner to provision isolated test fixtures.");
  return JSON.parse(readFileSync(location, "utf8"));
}
export function kc(command: string, data: Record<string, unknown> = {}): Record<string, unknown> {
  try {
    const output = execFileSync(
      "uv",
      [
        "run",
        "--no-project",
        "python",
        path.join(root, ".agents-config/skills/ops/keycloak-admin/scripts/keycloak.py"),
        "--env-file",
        process.env.AUTOMATION_ENV_FILE!,
        command,
      ],
      {
        input: JSON.stringify({ manifestPath: process.env.PW_FIXTURE_MANIFEST, ...data }),
        stdio: ["pipe", "pipe", "pipe"],
        encoding: "utf8",
        windowsHide: true,
      }
    );
    return JSON.parse(output);
  } catch {
    throw new Error("Fixture operation failed; raw output suppressed.");
  }
}
export async function login(page: Page, account: Account, target: string = routes.usersDashboard) {
  await page.goto(target);
  await page.locator("#username").fill(account.username);
  await page.locator("#password").fill(account.password);
  await page.locator("#kc-login").click();
  await page.waitForURL((url) => url.origin === new URL(process.env.PW_BASE_URL!).origin);
}
export const test = base.extend({
  page: async ({ page }, use, info) => {
    await use(page);
    if (info.status !== info.expectedStatus && page.url().startsWith(process.env.PW_BASE_URL!)) {
      // Capture only synthetic app pages, never Keycloak forms or reset/email links.
      const folder = path.join(process.env.PW_RUN_DIR!, "screenshots");
      mkdirSync(folder, { recursive: true });
      await page
        .screenshot({
          path: path.join(folder, info.testId.replace(/[^a-zA-Z0-9_-]/g, "_") + ".png"),
          fullPage: true,
        })
        .catch(() => {});
    }
  },
});
export { expect };
