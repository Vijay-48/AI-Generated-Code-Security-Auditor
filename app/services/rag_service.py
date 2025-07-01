import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import json

class RAGRemediationService:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(allow_reset=True)
        )
        self.collection = self.client.get_or_create_collection("vulnerability_remediation")
        
        if self.collection.count() == 0:
            self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        patterns = [
            {
                "cwe_id": "CWE-78",
                "title": "Command Injection",
                "pattern": "os.system call with user input",
                "remediation": (
                    "Use subprocess without shell=True:\n"
                    "import subprocess\n"
                    "subprocess.run(['ls', dir], check=True)"
                ),
                "languages": ["python"]
            },
            {
                "cwe_id": "CWE-89",
                "title": "SQL Injection",
                "pattern": "Raw SQL query with string formatting",
                "remediation": (
                    "Use parameterized queries:\n"
                    "cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
                ),
                "languages": ["python", "java"]
            },
            {
                "cwe_id": "CWE-79",
                "title": "Cross-Site Scripting (XSS)",
                "pattern": "Unescaped user output in HTML",
                "remediation": (
                    "Escape user input:\n"
                    "from html import escape\n"
                    "output = f'<div>{escape(user_input)}</div>'"
                ),
                "languages": ["python", "javascript"]
            }
        ]
        
        for pattern in patterns:
            self.add_remediation_pattern(pattern)

    def add_remediation_pattern(self, pattern: Dict[str, Any]):
        embedding_text = f"{pattern['title']} {pattern['pattern']}"
        embedding = self.embedder.encode([embedding_text])[0].tolist()
        
        self.collection.add(
            embeddings=[embedding],
            documents=[pattern['remediation']],
            metadatas=[{
                "cwe_id": pattern["cwe_id"],
                "title": pattern["title"],
                "languages": json.dumps(pattern["languages"])
            }],
            ids=[f"{pattern['cwe_id']}-{pattern['title']}"]
        )

    def retrieve_remediation(self, vulnerability: Dict[str, Any], top_k: int = 2) -> List[Dict[str, Any]]:
        query_text = f"{vulnerability['title']} {vulnerability['cwe_id']}"
        query_embedding = self.embedder.encode([query_text])[0].tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        remediation_patterns = []
        for i in range(len(results["documents"][0])):
            pattern = {
                "remediation_code": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "similarity": 1 - results["distances"][0][i]
            }
            remediation_patterns.append(pattern)
            
        return remediation_patterns