import os
import pdfplumber
import faiss
import numpy as np
import pandas as pd
import json
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# ===============================
# 1. LOAD PDF & EXTRACT TEXT
# ===============================
pdf_path = r"hkj.pdf"   # PDF same folder me honi chahiye

# ---- FILE EXIST CHECK ----
if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"❌ PDF file not found: {pdf_path}")

full_text = ""
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

# ---- TEXT CHECK ----
if len(full_text.strip()) == 0:
    raise ValueError("❌ No text extracted from PDF. PDF may be scanned or empty.")

print("✅ PDF text extracted successfully")

# ===============================
# 2. TEXT CHUNKING (SAFE)
# ===============================
chunks = [
    line.strip()
    for line in full_text.split("\n")
    if len(line.strip()) > 5
]

if len(chunks) == 0:
    raise ValueError("❌ No valid text chunks created")

print(f"✅ Total chunks created: {len(chunks)}")

# ===============================
# 3. CREATE EMBEDDINGS
# ===============================
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embed_model.encode(chunks)

# ---- EMBEDDING CHECK ----
if len(embeddings.shape) != 2:
    raise ValueError("❌ Embeddings not generated properly")

print("✅ Embeddings created")

# ===============================
# 4. STORE IN FAISS VECTOR DB
# ===============================
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

print("✅ FAISS index created")

# ===============================
# 5. USER QUERY (RAG)
# ===============================
query = "Extract roll number, name and status of all students"
query_embedding = embed_model.encode([query])

D, I = index.search(np.array(query_embedding), k=10)

context = " ".join([chunks[i] for i in I[0]])

if len(context.strip()) == 0:
    raise ValueError("❌ No relevant context retrieved")

print("✅ Relevant context retrieved")

# ===============================
# 6. LOAD LLM (TEXT GENERATION)
# ===============================
llm = pipeline(
    "text-generation",
    model="google/flan-t5-base",
    max_length=512
)

prompt = f"""
Extract student details from the text below.

Return ONLY JSON in this exact format:
[
  {{"roll": "...", "name": "...", "status": "..."}}
]

Text:
{context}
"""

llm_output = llm(prompt)[0]["generated_text"]

# ===============================
# 7. CLEAN JSON OUTPUT (SAFE)
# ===============================
json_start = llm_output.find("[")
json_end = llm_output.rfind("]") + 1

if json_start == -1 or json_end == -1:
    raise ValueError("❌ JSON not found in LLM output")

json_data = llm_output[json_start:json_end]

try:
    students = json.loads(json_data)
except json.JSONDecodeError:
    raise ValueError("❌ Failed to parse JSON output")

if len(students) == 0:
    raise ValueError("❌ No student data extracted")

print("✅ Student data extracted")

# ===============================
# 8. CONVERT TO EXCEL
# ===============================
df = pd.DataFrame(students)
df.columns = ["Roll_Number", "Name", "Status"]

output_file = "students_output.xlsx"
df.to_excel(output_file, index=False)

print("🎉 Excel file generated successfully:", output_file)
