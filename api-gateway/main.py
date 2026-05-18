from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field
import httpx
import os
import time

app = FastAPI(title="AI Platform API Gateway")
Instrumentator().instrument(app).expose(app)

VLLM_URL = os.environ["VLLM_URL"]
VLLM_MODEL = os.environ.get("VLLM_MODEL", "distilgpt2")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
NGROK_HEADERS = {"ngrok-skip-browser-warning": "true"}


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    embedding: list[float] = Field(default_factory=lambda: [0.0] * 384)


@app.post("/api/v1/chat")
async def chat(body: ChatRequest):
    start = time.time()
    context = []

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            search_resp = await client.post(
                f"{QDRANT_URL}/collections/documents/points/search",
                json={"vector": body.embedding, "limit": 3},
            )
            if search_resp.status_code == 200:
                context = search_resp.json().get("result", [])
    except httpx.HTTPError:
        context = []

    prompt = f"Context: {context}\n\nQuery: {body.query}"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            llm_resp = await client.post(
                f"{VLLM_URL}/v1/chat/completions",
                headers=NGROK_HEADERS,
                json={
                    "model": VLLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            llm_resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {exc}") from exc

    latency = (time.time() - start) * 1000
    result = llm_resp.json()

    return {
        "answer": result["choices"][0]["message"]["content"],
        "latency_ms": round(latency, 2),
        "model": result["model"],
    }


@app.get("/health")
def health():
    return {"status": "ok"}
