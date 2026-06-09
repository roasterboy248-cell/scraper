from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="Scrapling API", description="Web scraping API powered by Scrapling")


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Scrapling API</title>
        <style>
            body { font-family: sans-serif; max-width: 700px; margin: 60px auto; padding: 0 20px; background: #f9f9f9; }
            h1 { color: #333; }
            input { width: 70%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 6px; }
            button { padding: 10px 20px; font-size: 16px; background: #4f46e5; color: white; border: none; border-radius: 6px; cursor: pointer; margin-left: 8px; }
            button:hover { background: #4338ca; }
            pre { background: #1e1e1e; color: #d4d4d4; padding: 20px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; max-height: 500px; overflow-y: auto; }
            .loading { color: #888; font-style: italic; }
            .endpoint { background: #e0e7ff; padding: 12px 16px; border-radius: 6px; margin: 10px 0; font-family: monospace; }
        </style>
    </head>
    <body>
        <h1>🕷️ Scrapling API</h1>
        <p>A live web scraping API. Enter any URL below to extract its text content.</p>

        <h3>Try it out</h3>
        <input id="urlInput" type="text" placeholder="https://example.com" value="https://example.com" />
        <button onclick="scrape()">Scrape</button>

        <div id="output" style="margin-top:20px;"></div>

        <h3>API Endpoints</h3>
        <div class="endpoint">GET /scrape?url=https://example.com</div>
        <div class="endpoint">GET /scrape?url=https://example.com&amp;selector=h1</div>
        <div class="endpoint">GET /health</div>
        <div class="endpoint">GET /docs &nbsp;← Interactive API docs</div>

        <script>
            async function scrape() {
                const url = document.getElementById('urlInput').value;
                const output = document.getElementById('output');
                if (!url) return;
                output.innerHTML = '<p class="loading">Scraping... please wait ⏳</p>';
                try {
                    const res = await fetch('/scrape?url=' + encodeURIComponent(url));
                    const data = await res.json();
                    output.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (e) {
                    output.innerHTML = '<pre style="color:red">Error: ' + e.message + '</pre>';
                }
            }
        </script>
    </body>
    </html>
    """


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/scrape")
def scrape(
    url: str = Query(..., description="The URL to scrape"),
    selector: str = Query(None, description="Optional CSS selector to target specific elements")
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
        else:
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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
