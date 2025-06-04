import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from api.v1.routers import router_v1


load_dotenv()

app = FastAPI(
    root_path="/api",
    title="URL Alias Service",
    version="1.0",
)

app.include_router(router_v1)


@app.get("/ping", tags=["Ping"])
def health_check():
    return {"message": "pong"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("API_PORT", "8000")))
