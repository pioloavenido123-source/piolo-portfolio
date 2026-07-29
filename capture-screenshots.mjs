import { chromium } from 'playwright';
import { mkdirSync } from 'fs';

const dir = '/home/cmark/piolo-portfolio/screenshots';
mkdirSync(dir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

const sites = [
  { url: 'https://relaytask.com', name: 'relaytask' },
  { url: 'https://deskline.co', name: 'deskline' },
  { url: 'https://unifiedresident.com', name: 'unifiedresident' }
];

for (const site of sites) {
  try {
    await page.goto(site.url, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `${dir}/${site.name}.png`, fullPage: false });
    console.log(`OK: ${site.name} captured`);
  } catch(e) {
    console.log(`SKIP: ${site.name} - ${e.message.substring(0, 100)}`);
  }
}

await browser.close();
console.log('Done');