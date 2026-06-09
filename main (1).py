from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="Scrapling API")


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Scrapling API</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body { font-family: -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; }
            .card { background: #1e293b; border-radius: 16px; padding: 40px; max-width: 700px; width: 100%; box-shadow: 0 25px 50px rgba(0,0,0,0.4); }
            h1 { font-size: 2rem; margin-bottom: 8px; }
            p { color: #94a3b8; margin-bottom: 28px; }
            .row { display: flex; gap: 10px; margin-bottom: 20px; }
            input { flex: 1; padding: 12px 16px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; font-size: 15px; outline: none; }
            input:focus { border-color: #6366f1; }
            button { padding: 12px 22px; background: #6366f1; color: white; border: none; border-radius: 8px; font-size: 15px; cursor: pointer; white-space: nowrap; }
            button:hover { background: #4f46e5; }
            button:disabled { background: #334155; cursor: not-allowed; }
            pre { background: #0f172a; padding: 20px; border-radius: 10px; overflow: auto; max-height: 380px; font-size: 13px; line-height: 1.6; color: #a5f3fc; }
            .status { font-size: 13px; color: #64748b; margin-bottom: 10px; }
            .endpoints { margin-top: 24px; border-top: 1px solid #334155; padding-top: 20px; }
            .endpoints h3 { font-size: 13px; text-transform: uppercase; letter-spacing: 1px; color: #64748b; margin-bottom: 12px; }
            code { display: block; background: #0f172a; padding: 8px 12px; border-radius: 6px; font-size: 13px; color: #86efac; margin-bottom: 6px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🕷️ Scrapling API</h1>
            <p>Live web scraping. Enter any URL to extract its content.</p>
            <div class="row">
                <input id="url" type="text" placeholder="https://example.com" value="https://example.com" />
                <button id="btn" onclick="scrape()">Scrape</button>
            </div>
            <div class="status" id="status"></div>
            <pre id="out">Results will appear here...</pre>
            <div class="endpoints">
                <h3>API Endpoints</h3>
                <code>GET /scrape?url=https://example.com</code>
                <code>GET /scrape?url=https://example.com&selector=h1</code>
                <code>GET /health</code>
                <code>GET /docs  ← Interactive API docs (Swagger)</code>
            </div>
        </div>
        <script>
            async function scrape() {
                const url = document.getElementById('url').value.trim();
                const btn = document.getElementById('btn');
                const out = document.getElementById('out');
                const status = document.getElementById('status');
                if (!url) return;
                btn.disabled = true;
                btn.textContent = 'Scraping...';
                status.textContent = 'Fetching ' + url + ' ...';
                out.textContent = '';
                try {
                    const res = await fetch('/scrape?url=' + encodeURIComponent(url));
                    const data = await res.json();
                    out.textContent = JSON.stringify(data, null, 2);
                    status.textContent = res.ok ? '✅ Done' : '❌ Error';
                } catch (e) {
                    out.textContent = 'Error: ' + e.message;
                    status.textContent = '❌ Failed';
                } finally {
                    btn.disabled = false;
                    btn.textContent = 'Scrape';
                }
            }
            document.getElementById('url').addEventListener('keydown', e => { if (e.key === 'Enter') scrape(); });
        </script>
    </body>
    </html>
    """


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/scrape")
def scrape(
    url: str = Query(..., description="URL to scrape"),
    selector: str = Query(None, description="Optional CSS selector")
):
    try:
        from scrapling.fetchers import Fetcher
        fetcher = Fetcher(auto_match=False)
        page = fetcher.get(url, stealthy_headers=True)

        if selector:
            elements = page.css(selector)
            results = [el.text for el in elements if el.text]
            return {
                "url": url,
                "selector": selector,
                "count": len(results),
                "results": results
            }

        title = page.find("title")
        headings = page.css("h1, h2, h3")
        paragraphs = page.css("p")

        return {
            "url": url,
            "title": title.text if title else None,
            "headings": [h.text for h in headings if h.text][:10],
            "paragraphs": [p.text for p in paragraphs if p.text][:10],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
