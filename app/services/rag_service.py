from typing import Dict, Any, List

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except Exception:  # pragma: no cover - optional dependency
    chromadb = None
    ChromaSettings = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency
    SentenceTransformer = None

class RAGRemediationService:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self._patterns = self._default_patterns()
        self.embedder = None
        self.client = None
        self.col = None
        self.fallback_mode = True

        if SentenceTransformer is not None and chromadb is not None and ChromaSettings is not None:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=ChromaSettings(allow_reset=True)
            )
            self.col = self.client.get_or_create_collection(
                name="vuln_remediation",
                metadata={"description": "CWE to code fixes"}
            )
            if self.col.count() == 0:
                self._seed()
            self.fallback_mode = False

    def _default_patterns(self) -> List[Dict[str, str]]:
        return [
            {
                "cwe": "CWE-89",
                "title": "SQL Injection",
                "pattern": "unsanitized SQL",
                "remediation": (
                    "Use parameterized queries:\n"
                    "cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))"
                ),
            },
            {
                "cwe": "CWE-79",
                "title": "XSS",
                "pattern": "unescaped HTML",
                "remediation": (
                    "Escape output: from html import escape\n"
                    "return f'<div>{escape(user)}</div>'"
                ),
            },
        ]

    def _seed(self):
        for p in self._patterns:
            text = f"{p['title']} {p['pattern']}"
            emb = self.embedder.encode([text])[0].tolist()
            self.col.add(
                embeddings=[emb],
                documents=[p['remediation']],
                metadatas=[{"cwe":p['cwe']}],
                ids=[p['cwe']]
            )

    def retrieve_remediation(self, vuln: Dict[str, Any], top_k: int = 2) -> List[Dict[str, Any]]:
        if self.fallback_mode:
            cwe_id = str(vuln.get('cwe_id', '')).upper()
            title = str(vuln.get('title', '')).lower()
            out = []
            for p in self._patterns:
                score = 0.0
                if cwe_id and p['cwe'] == cwe_id:
                    score = 1.0
                elif p['title'].lower() in title:
                    score = 0.8

                if score > 0:
                    out.append({
                        "remediation_code": p['remediation'],
                        "metadata": {"cwe": p['cwe']},
                        "similarity": score,
                    })

            if not out:
                out.append({
                    "remediation_code": "Validate and sanitize untrusted input, use parameterized APIs, and avoid unsafe dynamic execution.",
                    "metadata": {"cwe": cwe_id or "UNKNOWN"},
                    "similarity": 0.5,
                })

            return out[:top_k]

        query = f"{vuln.get('title', '')} {vuln.get('cwe_id', '')}"
        emb = self.embedder.encode([query])[0].tolist()
        res = self.col.query(
            query_embeddings=[emb],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        out = []
        for doc, meta, dist in zip(res['documents'][0], res['metadatas'][0], res['distances'][0]):
            out.append({
                "remediation_code": doc,
                "metadata": meta,
                "similarity": 1 - dist
            })
        return out
