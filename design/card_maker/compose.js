// 실행: node design/card_maker/compose.js (Playwright 필요)
const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 500, height: 1200 } });
  await p.goto('file://' + __dirname + '/compose.html'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const path = require('path'), out = path.join(__dirname, '..', '..', 'assets');
  // PNG로 저장 후 WebP 변환: python3 -c "from PIL import Image; Image.open('x.png').save('x.webp', quality=88)"
  await (await p.$('#c1')).screenshot({ path: path.join(out, 'card_mouse.png'), omitBackground: true });
  await (await p.$('#c2')).screenshot({ path: path.join(out, 'card_chupa.png'), omitBackground: true });
  await b.close();
})();
