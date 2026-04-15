import { test, expect } from "@playwright/test";

test("home muestra chat y navegación", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Chat de soporte/i })).toBeVisible();
  await expect(page.getByRole("navigation")).toContainText("Ingesta");
});

test("flujo: subir archivo de texto y ver listado", async ({ page }) => {
  await page.goto("/upload");
  await expect(page.getByText("Subir documento")).toBeVisible();
});
