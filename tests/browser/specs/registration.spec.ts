import { test, expect, fixtures, kc, routes, login } from "../support";
import type { APIRequestContext } from "@playwright/test";
async function emailLink(request: APIRequestContext, address: string): Promise<string> {
  let found = "";
  await expect
    .poll(
      async () => {
        const response = await request.get(process.env.PW_MAILPIT_URL + "/api/v1/search", {
          params: { query: "to:" + address },
        });
        const data = await response.json();
        for (const message of data.messages || []) {
          if (!(message.To || []).some((to: { Address: string }) => to.Address === address))
            continue;
          const details = await (
            await request.get(process.env.PW_MAILPIT_URL + "/api/v1/message/" + message.ID)
          ).json();
          const content = String(details.HTML || details.Text || "");
          const matches = content.match(/https?:[^\s<>"']+/g) || [];
          const link = matches
            .map((value) => value.replaceAll("&amp;", "&"))
            .find((value) => {
              const url = new URL(value);
              return (
                url.origin === new URL(process.env.KEYCLOAK_ISSUER!).origin &&
                url.pathname.includes("/login-actions/")
              );
            });
          if (link) {
            found = link;
            return true;
          }
        }
        return false;
      },
      { timeout: 30_000, message: "Expected synthetic account email did not arrive" }
    )
    .toBe(true);
  return found;
}
test("self-registration verifies email, requires approval, and then logs in", async ({
  page,
  request,
}) => {
  const account = fixtures().registration;
  await page.goto(routes.authRegister);
  if (await page.locator("#username").count())
    await page.locator("#username").fill(account.username);
  await page.locator("#email").fill(account.email);
  if (await page.locator("#firstName").count()) await page.locator("#firstName").fill("Automation");
  if (await page.locator("#lastName").count()) await page.locator("#lastName").fill("Fixture");
  await page.locator("#password").fill(account.password);
  await page.locator("#password-confirm").fill(account.password);
  await page.getByRole("button", { name: /register/i }).click();
  await expect
    .poll(() => {
      try {
        return typeof kc("fixtures-adopt-registration").id === "string";
      } catch {
        return false;
      }
    })
    .toBe(true);
  await page.goto(await emailLink(request, account.email));
  await expect
    .poll(() => kc("fixtures-status"))
    .toMatchObject({ emailVerified: true, enabled: false, awaitingApproval: true });
  kc("fixtures-approve-registration");
  await page.context().clearCookies();
  await login(page, fixtures().registration);
  // Approval preserves realm defaults; the separate role matrix tests exact grants.
  await expect(page).toHaveURL(
    (url) =>
      url.origin === new URL(process.env.PW_BASE_URL!).origin &&
      [routes.usersDashboard, routes.forbidden].some((target) => target === url.pathname)
  );
  await expect(page.getByRole("main")).toBeVisible();
});
test("forgot-password email resets a disposable account", async ({ page, request }) => {
  const account = fixtures().users.reset;
  await page.goto(routes.authLoginWithPrompt);
  await page.getByRole("link", { name: /forgot.*password/i }).click();
  await page.locator("#username").fill(account.username);
  await page.getByRole("button", { name: /submit/i }).click();
  await page.goto(await emailLink(request, account.email));
  const password = account.password + "Reset1!";
  await page.locator("#password-new").fill(password);
  await page.locator("#password-confirm").fill(password);
  await page.getByRole("button", { name: /submit/i }).click();
  await page.context().clearCookies();
  await login(page, { ...account, password });
  await expect(page.getByRole("main")).toBeVisible();
});
