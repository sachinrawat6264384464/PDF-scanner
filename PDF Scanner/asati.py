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
pdf_path = "hkj.pdf"

full_text = ""
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

# ===============================
# 2. TEXT CHUNKING
# ===============================
chunks = full_text.split("\n")

# Remove empty lines
chunks = [chunk for chunk in chunks if len(chunk.strip()) > 5]

# ===============================
# 3. CREATE EMBEDDINGS
# ===============================
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embed_model.encode(chunks)

# ===============================
# 4. STORE IN FAISS VECTOR DB
# ===============================
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

# ===============================
# 5. USER QUERY (RAG)
# ===============================
query = "Extract roll number, name and status of all students"
query_embedding = embed_model.encode([query])

D, I = index.search(np.array(query_embedding), k=10)

context = " ".join([chunks[i] for i in I[0]])

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
# 7. CLEAN JSON OUTPUT
# ===============================
json_start = llm_output.find("[")
json_end = llm_output.rfind("]") + 1

json_data = llm_output[json_start:json_end]

students = json.loads(json_data)

# ===============================
# 8. CONVERT TO EXCEL
# ===============================
df = pd.DataFrame(students)
df.columns = ["Roll_Number", "Name", "Status"]

output_file = "students_output.xlsx"
df.to_excel(output_file, index=False)

print("✅ Excel file generated:", output_file)
