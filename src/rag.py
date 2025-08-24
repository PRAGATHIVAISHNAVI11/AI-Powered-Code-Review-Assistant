import os, glob
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class LocalRAG:
    def __init__(self, corpus_dir: str, embed_model: str):
        self.corpus_dir = corpus_dir
        self.model = SentenceTransformer(embed_model)
        self.docs: List[str] = []
        self.paths: List[str] = []
        self.index = None

    def build(self):
        files = glob.glob(os.path.join(self.corpus_dir, "**/*.md"), recursive=True)
        self.docs, self.paths = [], []
        for fp in files:
            with open(fp, "r", encoding="utf-8") as f:
                text = f.read()
            # chunk by headings or paragraphs (simple split)
            chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
            for c in chunks:
                self.docs.append(c)
                self.paths.append(os.path.basename(fp))

        embs = self.model.encode(self.docs, convert_to_numpy=True, normalize_embeddings=True)
        dim = embs.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embs)

    def query(self, text: str, k: int = 5) -> List[Dict[str, Any]]:
        q = self.model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        scores, idxs = self.index.search(q, k)
        out = []
        for score, idx in zip(scores[0], idxs[0]):
            out.append({"score": float(score), "doc": self.docs[idx], "path": self.paths[idx]})
        return out
