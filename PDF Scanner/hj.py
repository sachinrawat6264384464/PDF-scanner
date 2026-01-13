import re
import json
import pdfplumber
import pytesseract
import pandas as pd
import numpy as np
import faiss

from pdf2image import convert_from_path
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# ===============================
# CONFIG
# ===============================
PDF_PATH = r"hkj.pdf"

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\Dell 5490T\Desktop\poppler-25.12.0\Library\bin"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# ===============================
# 1. TEXT EXTRACTION (PDF + OCR)
# ===============================
full_text = ""

with pdfplumber.open(PDF_PATH) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

if not full_text.strip():
    print("⚠️ No text found → Applying OCR")
    images = convert_from_path(PDF_PATH, poppler_path=POPPLER_PATH)
    for img in images:
        full_text += pytesseract.image_to_string(img) + "\n"

if not full_text.strip():
    raise ValueError("❌ PDF text + OCR both failed")

print("✅ Text extracted successfully")

# ===============================
# 2. CHUNKING
# ===============================
chunks = [line.strip() for line in full_text.split("\n") if len(line.strip()) > 5]
print(f"✅ Chunks created: {len(chunks)}")

# ===============================
# 3. RAG (FAISS)
# ===============================
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embed_model.encode(chunks, convert_to_numpy=True)

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

query = "Extract student details like roll number, name, status, linkedin, github"
q_emb = embed_model.encode([query], convert_to_numpy=True)

_, I = index.search(q_emb, k=10)
context = " ".join(chunks[i] for i in I[0])

# ===============================
# 4. DOCUMENT TYPE DETECTION
# ===============================
is_resume = bool(re.search(r"linkedin|github", full_text, re.I))
is_marksheet = bool(re.search(r"pass|fail", full_text, re.I))

print("📄 Document type:", "Resume" if is_resume else "Marksheet")

# ===============================
# 5. LLM (OPTIONAL)
# ===============================
llm = pipeline("text2text-generation", model="google/flan-t5-base")

prompt = f"""
Extract structured student data.

Return JSON only.

Text:
{context}
"""

llm_output = llm(prompt, max_length=512)[0]["generated_text"]

# ===============================
# 6. TRY JSON PARSE
# ===============================
students = []
try:
    students = json.loads(llm_output)
except:
    students = []

# ===============================
# 7. REGEX FALLBACK (REAL LOGIC)
# ===============================
# ===============================
# 7. REGEX FALLBACK (FIXED)
# ===============================
if not students:
    print("⚠️ LLM failed → Using REGEX")

    students = []

    linkedin_pattern = r"(linkedin\s*[\.:]?\s*com\s*/\s*in\s*/\s*[A-Za-z0-9\-_/]+)"
    github_pattern   = r"(github\s*[\.:]?\s*com\s*/\s*[A-Za-z0-9\-_/]+)"

    linkedin_links = []
    github_links = []

    for line in chunks:
        for l in re.findall(linkedin_pattern, line, re.I):
            linkedin_links.append("https://" + l.replace(" ", ""))
        for g in re.findall(github_pattern, line, re.I):
            github_links.append("https://" + g.replace(" ", ""))

    max_len = max(len(linkedin_links), len(github_links))

    for i in range(max_len):
        students.append({
            "LinkedIn": linkedin_links[i] if i < len(linkedin_links) else "",
            "GitHub": github_links[i] if i < len(github_links) else ""
        })

if not students:
    raise ValueError("❌ No student data detected")

# ===============================
# 8. EXCEL EXPORT
# ===============================
df = pd.DataFrame(students)
df.to_excel("students_output.xlsx", index=False)

print("🎉 Excel Generated Successfully → students_output.xlsx")
