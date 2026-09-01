from fastapi import FastAPI

app = FastAPI(title="PayGuard AI Health Service")

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "payguard-ai-api",
        "version": "1.0.0"
    }
