# Source Ledger
A local-first search evidence notebook for people who need receipts, not an automatic factual verdict. Built with AI assistance for the SerpApi India Hackathon's Knowledge & Public Interest track.

## Verified status
On October 4, 2026, the local app ran two genuine SerpApi Google searches using a free account, returned real result records, reused the persistent cache without another provider attempt, retained review notes through refresh and exported JSON. The final demo uses a documentation query; its original search ID is `6ac1d07f1b6c6e0f3f3d5b70`, retrieved at `2026-10-04T04:05:20Z`. The notebook marks one source reviewed only after that source was inspected. Search relevance varies: an earlier longer heat-wave query returned mostly irrelevant leads, which is a limitation, not proof of factual accuracy. Four backend tests and browser tests use labeled fixtures. No paid searches or earnings claimed.

## Demo
[Watch the 17-second genuine demo](https://drive.google.com/file/d/1WyJCHlZbm6rqUwl8Z4UIbLTQXo_QWb-1/view). It shows the cached real documentation search, an inspected-source note and reviewed filter. Cache replay does not make another provider call.

## Run
Python 3.10+, standard library only:
```sh
export SERPAPI_KEY='your-private-key'
python3 app.py
```
Open http://127.0.0.1:8765. Never commit your key or show it in a demo. No key goes to the browser.

## Workflow
1. Enter a public search query. Do not search private data.
2. SerpApi Google results become unverified leads, each retaining its source URL, domain, snippet, retrieval timestamp, search ID and metadata fingerprint.
3. Open the original source. Record the relevant passage and any caveat. Explicitly mark what you reviewed.
4. Build a notebook across searches. Filter unreviewed leads and export JSON or CSV.

## Engineering choices
- Persistent SQLite exact-query cache, so repeating a query across server restarts does not spend another provider call. The original retrieval timestamp is retained; cached does not mean current.
- Persistent 200-attempt local cap. An attempt is reserved before network I/O; failures count too. There are no automatic retries or paid overage features. Check your account allowance separately because other apps can use it.
- Browser local storage retains notes through refresh. No notes sent to the provider. Notes are not encrypted; use only public research.
- HTML text escaped, links limited to HTTP(S), noopener on new tabs, foreign browser origins rejected, generic provider errors prevent accidental key disclosure. CSV cells starting with formula characters are neutralized.
- A lead hash fingerprints the retrieved search record, NOT the original page or factual truth.
- No LLM is required to run the app. Human review is explicit, never presented as automated verification.

## Tests
```sh
python3 test_app.py
```
Four backend fixture tests cover missing key/no calls, persistent cache/one call, cap/no calls and failed-provider key redaction/budget. They make no real provider calls.
Optional browser fixture tests need Playwright and Chrome:
```sh
pip install playwright
python3 ui_test.py
```
These cover first-record notes/review, HTML escaping, refresh persistence, filters, JSON export and deduplication. Test UI screenshots are not demo evidence. The Chrome path in that test may need adjusting on your machine.

## Limits
Single-user local prototype, not multi-user production hosting. Cache has no automatic refresh, and notes are unencrypted local browser data. Snippets can be stale, truncated or wrong. The app does not fetch pages, assess credibility or verify claims. Human source checks remain required. Export files can contain your research; keep them private unless intentionally shared.

## AI disclosure
Code, interface copy and documentation were developed with AI assistance. Tests and claims are reviewed separately; no fabricated usage, user study, benchmark, professional experience or award is claimed.
