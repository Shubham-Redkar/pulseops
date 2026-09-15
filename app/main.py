from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def home():
    return {
        "service": "PulseOps API",
        "message": "API is live and ready to serve requests",
        "status": "operational",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
