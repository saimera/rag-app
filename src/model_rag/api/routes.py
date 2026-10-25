from fastapi import APIRouter
from pydantic import BaseModel

from ..services.query_service import answer_question, get_cited_chunks

router = APIRouter()

class AskRequest(BaseModel):
    query: str

@router.post("/ask")
def ask(request: AskRequest):
    answer, chunks = answer_question(request.query)
    references = [
        {
            "number": n,
            "title": c["title"],
            "page_no": c["page_no"],
            "url": f"{c['source_url']}#page={c['page_no']}",
        }
        for n, c in get_cited_chunks(answer, chunks)
    ]
    return {"answer": answer, "references": references}