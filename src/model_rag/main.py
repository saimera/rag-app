from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .api.routes import router

app = FastAPI(title="Model RAG")
app.include_router(router)

TEMPLATE_PATH = Path(__file__).parent / "templates" / "app.html"


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(TEMPLATE_PATH)