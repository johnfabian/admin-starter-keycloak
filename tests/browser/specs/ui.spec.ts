import AxeBuilder from "@axe-core/playwright";
import { test, expect, login, fixtures, routes } from "../support";
test("desktop navigation, themes and keyboard controls", async ({ page }) => {
  await login(page, fixtures().users.users);
  await expect(page.getByRole("complementary", { name: "Dashboard navigation" })).toBeVisible();
  await page.getByRole("button", { name: "Toggle navigation" }).click();
  await page.getByRole("button", { name: "Toggle navigation" }).click();
  const mode = page.getByRole("button", { name: /Switch to (light|dark) mode/ });
  const before = await mode.getAttribute("aria-label");
  await mode.click();
  await page.reload();
  await expect(mode).not.toHaveAttribute("aria-label", before!);
  await page.getByRole("button", { name: /Accent theme settings/ }).click();
  await page.getByRole("menuitemradio", { name: "Purple" }).click();
  await page.goto(routes.profile);
  await expect(page.getByRole("button", { name: /current theme: Purple/ })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("button", { name: /current theme: Purple/ })).toBeVisible();
  const account = page.getByRole("button", { name: "Open account menu" });
  await account.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByRole("menuitem", { name: "Account", exact: true })).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(account).toBeFocused();
  // Move to the preceding app control; Tab from the final header control can leave the document.
  await page.keyboard.press("Shift+Tab");
  const focused = await page.evaluate(() => {
    const el = document.activeElement as HTMLElement;
    const rect = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    return (
      rect.width > 0 &&
      rect.height > 0 &&
      (style.outlineStyle !== "none" || style.boxShadow !== "none")
    );
  });
  expect(focused).toBe(true);
});
test("system theme follows device preference", async ({ page, context }) => {
  await context.addCookies([
    { name: "admin-starter-color-mode", value: "system", url: process.env.PW_BASE_URL! },
  ]);
  await page.emulateMedia({ colorScheme: "dark" });
  await login(page, fixtures().users.users);
  await expect(page.getByRole("button", { name: "Switch to light mode" })).toBeVisible();
  await page.emulateMedia({ colorScheme: "light" });
  await expect(page.getByRole("button", { name: "Switch to dark mode" })).toBeVisible();
});
test("mobile navigation remains reachable and fits viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page, fixtures().users.users);
  await page.getByRole("button", { name: "Open navigation" }).click();
  const nav = page.getByRole("complementary", { name: "Dashboard navigation" });
  await expect(nav).toBeInViewport();
  await nav.getByRole("link", { name: "Profile", exact: true }).click();
  await expect(page).toHaveURL(new URL(routes.profile, process.env.PW_BASE_URL!).toString());
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});
test("automated accessibility checks on public and signed-in pages", async ({ page }) => {
  for (const target of [routes.home, routes.forbidden]) {
    await page.goto(target);
    const result = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    expect(result.violations.map((v) => v.id)).toEqual([]);
  }
  await login(page, fixtures().users.users);
  const result = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(result.violations.map((v) => v.id)).toEqual([]);
});
