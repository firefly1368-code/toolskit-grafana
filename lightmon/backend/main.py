from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, Counter, Histogram
import httpx, os, time

app = FastAPI(title="LightMon API", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics endpoint agar tidak 404
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

PROMETHEUS_URL   = os.getenv("PROMETHEUS_URL",   "http://prometheus:9090")
LOKI_URL         = os.getenv("LOKI_URL",         "http://loki:3100")
ALERTMANAGER_URL = os.getenv("ALERTMANAGER_URL", "http://alertmanager:9093")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "lightmon-backend", "version": "4.0"}


@app.get("/api/metrics/query")
async def query_metrics(q: str):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": q})
            return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/targets")
async def get_targets():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{PROMETHEUS_URL}/api/v1/targets")
            return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
async def get_alerts():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{ALERTMANAGER_URL}/api/v2/alerts")
            return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    """Cek status semua komponen monitoring."""
    results = {}
    checks = {
        "prometheus": f"{PROMETHEUS_URL}/-/ready",
        "loki":       f"{LOKI_URL}/ready",
        "alertmanager": f"{ALERTMANAGER_URL}/-/ready",
    }
    async with httpx.AsyncClient(timeout=5) as client:
        for name, url in checks.items():
            try:
                r = await client.get(url)
                results[name] = "healthy" if r.status_code == 200 else "degraded"
            except:
                results[name] = "unreachable"
    return results
