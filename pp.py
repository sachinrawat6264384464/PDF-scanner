import os
import faiss
import numpy as np
import pandas as pd
from PyPDF2 import PdfReader
import google.generativeai as genai
import json
import re
import sys

# =========================
# CONFIG
# =========================
GOOGLE_API_KEY = "AIzaSyBCVYWJE2wKnoFTE4oq_H0TQtuMx3hMpNY"
EMBED_MODEL = "models/gemini-embedding-001"
CHAT_MODEL = "gemini-2.0-flash"

try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"❌ Gemini configuration failed: {e}")

# =========================
# UTILS
# =========================
def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks

def get_embedding(text, task_type="retrieval_document"):
    try:
        result = genai.embed_content(
            model=EMBED_MODEL,
            content=text,
            task_type=task_type
        )
        return np.array(result['embedding'], dtype="float32")
    except Exception as e:
        print(f"❌ Embedding failed for model {EMBED_MODEL}: {e}")
        raise e

# =========================
# RAG CLASS
# =========================
class RAG:
    def __init__(self):
        self.text_chunks = []
        self.index = None

    def ingest_pdf(self, pdf_path):
        try:
            reader = PdfReader(pdf_path)
            raw_text = ""
            for page in reader.pages:
                if page.extract_text():
                    raw_text += page.extract_text() + "\n"
            
            if not raw_text.strip():
                print("❌ Document contains no extractable text!")
                return False

            self.text_chunks = chunk_text(raw_text)
            print(f"📄 PDF loaded. Split into {len(self.text_chunks)} chunks.")

            print("💡 Generating embeddings (Gemini API)...")
            embeddings = []
            for i, c in enumerate(self.text_chunks):
                embeddings.append(get_embedding(c))
                if (i+1) % 5 == 0: print(f"  Processed {i+1} chunks...")
            
            embeddings = np.array(embeddings, dtype="float32")
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
            self.index.add(embeddings)
            return True
        except Exception as e:
            print(f"❌ Ingestion failed: {e}")
            return False

    def retrieve(self, query, k=5):
        try:
            q_emb = get_embedding(query, task_type="retrieval_query").reshape(1, -1)
            _, indices = self.index.search(q_emb, k)
            return [self.text_chunks[i] for i in indices[0]]
        except Exception as e:
            print(f"❌ Retrieval failed: {e}")
            return []

    def extract_name_roll(self):
        # Using a more generic query since user says data is raw
        context_chunks = self.retrieve("list of students names and numbers")
        if not context_chunks:
            return []
            
        context_text = "\n".join(context_chunks)

        # Bug Fix: Escaped {{ and }} to avoid f-string ValueError
        prompt = f"""
You are an AI assistant. I have text from a PDF that contains student information (names, roll numbers, or IDs).
The data might not have clear labels, so look for patterns of names and numbers.
Extract the data into a STRICTOR JSON list of objects.

JSON format: [{{ "name": "VALUE", "roll": "VALUE" }}]

Text to process:
{context_text}
"""
        try:
            model = genai.GenerativeModel(CHAT_MODEL)
            response = model.generate_content(prompt)
            llm_text = response.text

            # Robust JSON extraction
            json_match = re.search(r"\[.*\]", llm_text, re.DOTALL)
            if json_match:
                records = json.loads(json_match.group(0))
                return records
            else:
                print(f"❌ No JSON data detected in Gemini's response.")
                return []
        except Exception as e:
            print(f"❌ Extraction Error: {e}")
            return []

    def save_to_excel(self, records, output_path="output.xlsx"):
        if records:
            try:
                df = pd.DataFrame(records)
                df.to_excel(output_path, index=False)
                print(f"✅ Excel generated: {output_path}")
            except Exception as e:
                print(f"❌ Excel saving failed: {e}. Tip: Try 'pip install openpyxl'")
        else:
            print("❌ No records to save")


if __name__ == "__main__":
    pdf_path = input("Enter path of PDF (e.g., index.pdf): ").strip()
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found at: {os.path.abspath(pdf_path)}")
        sys.exit()

    rag = RAG()
    print("📄 Ingesting PDF...")
    if rag.ingest_pdf(pdf_path):
        print("🤖 Extracting data...")
        records = rag.extract_name_roll()
        print("📊 Saving results...")
        rag.save_to_excel(records)
    else:
        print("❌ Script stopped due to ingestion error.")

