"""Browser fixture tests only. Never use this as an external-API demo."""
from playwright.sync_api import sync_playwright
import json
from pathlib import Path
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/opt/google/chrome/chrome',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':1280,'height':900});page.set_default_timeout(5000)
 page.route('http://127.0.0.1:8765/',lambda r:r.fulfill(body=Path('index.html').read_text(),content_type='text/html'))
 fixture={'query':'fixture query','retrieved_utc':'fixture-only','search_id':'fixture-only','budget_used':1,'budget_limit':200,'cached':False,'results':[{'title':'<script>do not execute</script>','url':'https://example.com/','domain':'example.com','snippet':'UI fixture, not real source evidence','lead_hash':'fixture-only'}]}
 page.route('**/search',lambda r:r.fulfill(json=fixture));page.goto('http://127.0.0.1:8765/')
 page.locator('#q').fill('fixture query');page.locator('#search').click();page.wait_for_selector('.card')
 page.locator('[data-review="0"]').check();page.locator('[data-note="0"]').fill('Test note at index zero');out=page.evaluate('evidence')
 assert out[0]['review']=='user-reviewed' and out[0]['note']=='Test note at index zero',out
 assert page.locator('.card h2').inner_text()=='<script>do not execute</script>'
 page.reload();assert page.locator('[data-note="0"]').input_value()=='Test note at index zero'
 page.locator('#filter').select_option('unreviewed');assert page.locator('.card').count()==0;page.locator('#filter').select_option('all')
 with page.expect_download() as d:page.locator('#export').click()
 data=json.loads(Path(d.value.path()).read_text());assert data['records'][0]['note']=='Test note at index zero';assert data['format']=='source-ledger-v2'
 page.locator('#q').fill('fixture query');page.locator('#search').click();assert page.locator('.card').count()==1
 page.screenshot(path='/downloads/source-ledger-fixture-ui.png',full_page=True)
 page.set_viewport_size({'width':390,'height':844});page.screenshot(path='/downloads/source-ledger-mobile-fixture.png',full_page=True)
 print('UI tests: escaping, first-record review/note, refresh persistence, filters, JSON export, deduplication. Fixture only. All passed.')
 b.close()
