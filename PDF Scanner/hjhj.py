import os
import pdfplumber
import faiss
import numpy as np
import pandas as pd
import json
import pytesseract
from pdf2image import convert_from_path
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# ===============================
# CONFIG
# ===============================
pdf_path = r"hkj.pdf"

# ✅ Tesseract path (WINDOWS)
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# ✅ Poppler BIN path (MOST IMPORTANT FIX)
POPPLER_PATH = r"C:\Users\Dell 5490T\Desktop\poppler-25.12.0\Library\bin"

# ===============================
# 1. EXTRACT TEXT (PDF OR OCR)
# ===============================
full_text = ""

# ---- TRY NORMAL PDF TEXT ----
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

# ---- IF NO TEXT → OCR ----
if not full_text.strip():
    print("⚠️ No text found, applying OCR...")

    images = convert_from_path(
        pdf_path,
        poppler_path=POPPLER_PATH
    )

    for img in images:
        ocr_text = pytesseract.image_to_string(img)
        full_text += ocr_text + "\n"

# ---- FINAL CHECK ----
if not full_text.strip():
    raise ValueError("❌ OCR also failed. PDF quality too low.")

print("✅ Text extracted successfully")

# ===============================
# 2. TEXT CHUNKING
# ===============================
chunks = [
    line.strip()
    for line in full_text.split("\n")
    if len(line.strip()) > 5
]

if not chunks:
    raise ValueError("❌ No valid text chunks")

print(f"✅ Chunks created: {len(chunks)}")

# ===============================
# 3. EMBEDDINGS
# ===============================
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embed_model.encode(chunks, convert_to_numpy=True)

# ===============================
# 4. FAISS VECTOR DB
# ===============================
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# ===============================
# 5. RAG QUERY
# ===============================
query =  "Extract LinkedIn and GitHub of all students"
query_embedding = embed_model.encode([query], convert_to_numpy=True)

D, I = index.search(query_embedding, k=10)
context = " ".join(chunks[i] for i in I[0])

# ===============================
# 6. LLM (FLAN-T5)
# ===============================
llm = pipeline(
    "text-generation",
    model="google/flan-t5-base",
    max_length=512
)

prompt = f"""
Extract student details from the text below.

Return ONLY JSON:
[
  {{"LinkedIn": "...", "GitHub": "..."}}]

Text:
{context}
"""

llm_output = llm(prompt)[0]["generated_text"]

# ===============================
# 7. JSON CLEAN
# ===============================
json_start = llm_output.find("[")
json_end = llm_output.rfind("]") + 1

if json_start == -1 or json_end == -1:
    raise ValueError("❌ LLM did not return valid JSON")

students = json.loads(llm_output[json_start:json_end])

# ===============================
# 8. EXCEL EXPORT
# ===============================
df = pd.DataFrame(students)
df.columns = ["LinkedIn", "GitHub"]

output_file = "students_output.xlsx"
df.to_excel(output_file, index=False)

print("🎉 Excel generated successfully:", output_file)
