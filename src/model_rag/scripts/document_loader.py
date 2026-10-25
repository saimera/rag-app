from langchain_community.document_loaders import PyMuPDFLoader

pdf_path = "Claude Opus 5.5 System Card.pdf"  # apni file ka asli naam yahan likhein

def load_pdf(pdf_path: str):
    loader = PyMuPDFLoader(pdf_path)
    return loader.load()

# print("Total pages:", len(docs))
# print("Metadata sample:", docs[0].metadata)

# for i in [0, 9, 49]:
#     if i < len(docs):
#         d = docs[i]
#         print(f"\n--- page_no: {d.metadata['page'] + 1}, chars: {len(d.page_content)} ---")
#         print(d.page_content[:500])