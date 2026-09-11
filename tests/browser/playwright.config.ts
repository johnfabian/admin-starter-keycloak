import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./specs",
  outputDir: process.env.PW_RUN_DIR ? process.env.PW_RUN_DIR + "/results" : "./test-results",
  fullyParallel: false,
  preserveOutput: "never",
  workers: 1,
  retries: 0,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: [["./safe-reporter.ts"]],
  use: {
    baseURL: process.env.PW_BASE_URL,
    trace: "off",
    screenshot: "off",
    video: "off",
    actionTimeout: 15_000,
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
