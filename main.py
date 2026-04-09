from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import re
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_references(text):
    match = re.search(r'(references|bibliography|referencias)[\s\S]*', text, re.IGNORECASE)
    if not match:
        return []

    return [
        r.strip()
        for r in match.group(0).split("\n")
        if len(r.strip()) > 40
    ]

@app.get("/")
def root():
    return {"status": "API running"}

@app.head("/")
def root_head():
    return {}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    contents = await file.read()

    temp_file = "temp.pdf"
    with open(temp_file, "wb") as f:
        f.write(contents)

    with pdfplumber.open(temp_file) as pdf:
        text = "\n".join([page.extract_text() or "" for page in pdf.pages])

    refs = extract_references(text)

    os.remove(temp_file)

    return {
        "total": len(refs),
        "references": refs[:50]
    }
