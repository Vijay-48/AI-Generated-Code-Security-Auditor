import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from typing import Dict, Any, List

class RAGRemediationService:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(allow_reset=True)
        )
        self.col = self.client.get_or_create_collection(
            name="vuln_remediation",
            metadata={"description":"CWE → code fixes"}
        )
        if self.col.count() == 0:
            self._seed()

    def _seed(self):
        patterns = [
            {
                "cwe":"CWE-89","title":"SQL Injection",
                "pattern":"unsanitized SQL",
                "remediation":(
                    "Use parameterized queries:\n"
                    "cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))"
                )
            },
            {
                "cwe":"CWE-79","title":"XSS",
                "pattern":"unescaped HTML",
                "remediation":(
                    "Escape output: from html import escape\n"
                    "return f'<div>{escape(user)}</div>'"
                )
            }
        ]
        for p in patterns:
            text = f"{p['title']} {p['pattern']}"
            emb = self.embedder.encode([text])[0].tolist()
            self.col.add(
                embeddings=[emb],
                documents=[p['remediation']],
                metadatas=[{"cwe":p['cwe']}],
                ids=[p['cwe']]
            )

    def retrieve_remediation(self, vuln: Dict[str, Any], top_k: int = 2) -> List[Dict[str, Any]]:
        query = f"{vuln['title']} {vuln['cwe_id']}"
        emb = self.embedder.encode([query])[0].tolist()
        res = self.col.query(
            query_embeddings=[emb],
            n_results=top_k,
            include=['documents','metadatas','distances']
        )
        out = []
        for doc,meta,dist in zip(res['documents'][0], res['metadatas'][0], res['distances'][0]):
            out.append({
                "remediation_code": doc,
                "metadata": meta,
                "similarity": 1 - dist
            })
        return out
