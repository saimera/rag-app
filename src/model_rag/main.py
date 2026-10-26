from fastapi import FastAPI
from fastapi.responses import FileResponse

from .api.routes import router

app = FastAPI(title="Model RAG")
app.include_router(router)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse("src/model_rag/templates/app.html")