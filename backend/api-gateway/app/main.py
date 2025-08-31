# api-gateway/app/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from typing import Dict


app = FastAPI(title="FinTracker API Gateway", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Service URLs
SERVICES = {
    "auth": "http://localhost:8001",
    "portfolio": "http://localhost:8002",
    "news": "http://localhost:8003"
}


@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(request: Request, path: str):
    """Proxy requests to auth service"""
    return await proxy_request(request, "auth", path)


@app.api_route("/api/v1/portfolio/{path:path}", methods=["GET", "POST", "PUT", "DELETE"]) 
async def portfolio_proxy(request: Request, path: str):
    """Proxy requests to portfolio service"""
    return await proxy_request(request, "portfolio", path)


@app.api_route("/api/v1/market/news/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def news_proxy(request: Request, path: str):
    """Proxy requests to news service"""
    return await proxy_request(request, "news", path)


async def proxy_request(request: Request, service: str, path: str):
    """Generic proxy function"""
    service_url = SERVICES.get(service)
    if not service_url:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Fixed: Remove the service prefix and forward the path as expected by microservices
    url = f"{service_url}/api/v1/{path}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers={k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']},
                params=dict(request.query_params),
                content=await request.body()
            )
            
            # Return the response with proper status code and headers
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "api-gateway"}
