import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  timeout: 60000,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:4183",
    trace: "off",
    ...devices["Desktop Chrome"],
    launchOptions: { args: ["--enable-unsafe-swiftshader"] },
  },
  webServer: process.env.PLAYWRIGHT_BASE_URL
    ? undefined
    : {
        command: "npm run preview -- --host 127.0.0.1 --port 4183",
        url: "http://127.0.0.1:4183",
        reuseExistingServer: false,
      },
  reporter: "list",
});
