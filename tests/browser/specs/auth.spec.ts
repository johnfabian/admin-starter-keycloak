import { test, expect, fixtures, login, routes } from "../support";

const protectedRoutes = [
  routes.users,
  routes.usersDashboard,
  routes.profile,
  routes.settings,
  routes.apps,
  routes.appsDashboard,
  routes.todos,
  routes.admins,
  routes.adminsDashboard,
];
test("public splash and safe login initiation", async ({ page }) => {
  await page.goto(routes.home);
  await expect(page.getByRole("link", { name: /sign in/i }).first()).toBeVisible();
  await page.goto(routes.authLogin + "?returnTo=https%3A%2F%2Fexample.com");
  await expect(page.locator("#username")).toBeVisible();
  expect(new URL(page.url()).origin).toBe(new URL(process.env.KEYCLOAK_ISSUER!).origin);
  await page.goto(routes.authLoginWithPrompt);
  expect(new URL(page.url()).searchParams.get("prompt")).toBe("login");
  await expect(page.locator("#password")).toBeVisible();
});
test("anonymous protected routes initiate authentication", async ({ page }) => {
  for (const target of protectedRoutes) {
    await page.goto(target);
    await expect(page.locator("#username")).toBeVisible();
  }
});
test("callback preserves protected return path", async ({ page }) => {
  await login(page, fixtures().users.users, routes.profile);
  await expect(page).toHaveURL(new URL(routes.profile, process.env.PW_BASE_URL!).toString());
  await expect(page.getByRole("main")).toBeVisible();
});
for (const role of ["noRole", "users", "admins"] as const) {
  test(role + " authorization matrix", async ({ page }) => {
    await login(page, fixtures().users[role]);
    for (const target of protectedRoutes) {
      await page.goto(target);
      const denied = role === "noRole" || (role === "users" && target.startsWith(routes.admins));
      if (denied) {
        await expect(page).toHaveURL(
          new URL(routes.forbidden, process.env.PW_BASE_URL!).toString()
        );
      } else {
        await expect(page.getByRole("main")).toBeVisible();
        const expected =
          target === routes.users
            ? routes.usersDashboard
            : target === routes.apps
              ? routes.appsDashboard
              : target === routes.admins
                ? routes.adminsDashboard
                : target;
        await expect(page).toHaveURL(new URL(expected, process.env.PW_BASE_URL!).toString());
      }
    }
  });
}
test("session survives navigation and reload without browser tokens", async ({ page, context }) => {
  const payloads: string[] = [];
  page.on("response", async (response) => {
    if (
      response.url().startsWith(process.env.PW_BASE_URL!) &&
      /json|html|text\/x-script/.test(response.headers()["content-type"] || "")
    ) {
      const text = await response.text().catch(() => "");
      payloads.push(text);
    }
  });
  await login(page, fixtures().users.users);
  await page.goto(routes.settings);
  await page.reload();
  await expect(page.getByRole("button", { name: "Open account menu" })).toBeVisible();
  const browserData = await page.evaluate(() =>
    JSON.stringify({
      local: { ...localStorage },
      session: { ...sessionStorage },
      cookie: document.cookie,
      markup: document.documentElement.outerHTML,
    })
  );
  const forbidden =
    /eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|"(?:access_token|refresh_token)"\s*:/;
  expect(forbidden.test(browserData)).toBe(false);
  expect(payloads.some((value) => forbidden.test(value))).toBe(false);
  const sessionCookie = (await context.cookies()).find(
    (cookie) => cookie.name === "__admin_starter_session"
  );
  expect(Boolean(sessionCookie?.httpOnly)).toBe(true);
  expect(sessionCookie?.sameSite).toBe("Lax");
});
test("logout clears app session and protects subsequent navigation", async ({ page, context }) => {
  await login(page, fixtures().users.logout);
  await page.getByRole("button", { name: "Open account menu" }).click();
  await page.getByRole("menuitem", { name: /log ?out/i }).click();
  await page.waitForURL(
    (url) => url.origin !== new URL(process.env.PW_BASE_URL!).origin || url.pathname === routes.home
  );
  const confirm = page.getByRole("button", { name: /log ?out/i });
  if (
    new URL(page.url()).origin !== new URL(process.env.PW_BASE_URL!).origin &&
    (await confirm.count())
  )
    await confirm.click();
  await page.waitForURL(
    (url) => url.origin === new URL(process.env.PW_BASE_URL!).origin && url.pathname === routes.home
  );
  expect(
    (await context.cookies()).some((cookie) => cookie.name === "__admin_starter_session")
  ).toBe(false);
  await page.goto(routes.usersDashboard);
  await expect(page.locator("#username")).toBeVisible();
});
test("logout origin checks and sanitized public errors", async ({ request, page }) => {
  const result = await request.post(routes.authLogout, {
    headers: { Origin: "https://example.com" },
    maxRedirects: 0,
  });
  // React Router rejects cross-site document actions before the route-level guard.
  expect(result.status()).toBe(400);
  const missing = await page.goto("/automation-missing-page");
  expect(missing?.status()).toBe(404);
  await expect(page.getByText(/not found/i).first()).toBeVisible();
  await page.goto(routes.forbidden);
  await expect(page.getByText(/forbidden|access denied/i).first()).toBeVisible();
  const text = await page.locator("body").innerText();
  expect(/stack trace|postgresql:\/\/|client_secret|refresh_token/i.test(text)).toBe(false);
});
test("authenticated development error previews are sanitized", async ({ page }) => {
  await login(page, fixtures().users.users);
  await page.goto(routes.usersDashboardErrorPreview + "/500");
  await expect(page.getByRole("main")).toBeVisible();
  expect(
    /stack trace|postgresql:\/\/|client_secret/i.test(await page.locator("body").innerText())
  ).toBe(false);
});
