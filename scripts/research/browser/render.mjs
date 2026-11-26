// render.mjs <url> <out-prefix> [wait-seconds]
// Loads a page in headless Chromium, opens <details> sections and expands collapsed accordions
// (aria-expanded="false" buttons), then writes the visible text to <out-prefix>.txt and the HTML to
// <out-prefix>.html. For pages that only render with JavaScript.
// Bot checks: if the page is a CAPTCHA / "verify you are human" / Cloudflare / Imperva challenge, it writes
// nothing and exits 3 ("BLOCKED"). It never tries to solve or get around a challenge (CLAUDE.md rule 1).
import { chromium } from "playwright-core";
import { writeFileSync } from "node:fs";

const [url, out, wait = "4"] = process.argv.slice(2);
if (!url || !out) {
  console.error("usage: render.mjs <url> <out-prefix> [wait-seconds]");
  process.exit(2);
}
const BLOCK = /verify you are human|additional security check is required|i am human|just a moment\.\.\.|attention required|captcha|access denied|request unsuccessful\. incapsula/i;

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ locale: "en-GB" });
  const res = await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });
  await page.waitForTimeout(Number(wait) * 1000);
  const title = await page.title();
  const first = await page.evaluate(() => document.body?.innerText?.slice(0, 2000) ?? "");
  if (BLOCK.test(title) || BLOCK.test(first)) {
    console.log(`BLOCKED status=${res?.status()} title=${JSON.stringify(title)}`);
    process.exit(3);
  }
  // Open collapsed content so it is in the text (no clicks on links, forms or anything that navigates).
  await page.evaluate(() => {
    document.querySelectorAll("details").forEach((d) => (d.open = true));
    document.querySelectorAll('button[aria-expanded="false"]').forEach((b) => {
      if (!b.closest("form") && !b.closest("nav")) b.click();
    });
  });
  await page.waitForTimeout(1500);
  // Visible text, then the text of hidden tab panels / collapsed sections the page already loaded
  // (e.g. a "Non-Local Students" tab), each marked so a reader can see where it came from.
  const text = await page.evaluate(() => {
    const hidden = [...document.querySelectorAll('[role="tabpanel"], .tab-pane, .tabs-panel, [hidden], [aria-hidden="true"]')]
      .filter((el) => !el.closest("nav, header, footer, script, style") && el.textContent.trim().length > 40)
      .map((el) => el.textContent.replace(/\s+/g, " ").trim());
    return document.body.innerText + (hidden.length ? "\n\n[hidden sections]\n" + [...new Set(hidden)].join("\n") : "");
  });
  writeFileSync(`${out}.txt`, text);
  writeFileSync(`${out}.html`, await page.content());
  console.log(`OK status=${res?.status()} chars=${text.length}`);
} finally {
  await browser.close();
}
