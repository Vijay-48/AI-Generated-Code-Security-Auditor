from app.services.rag_service import RAGRemediationService

def seed_database():
    rag = RAGRemediationService()
    print(f"Database seeded with {rag.col.count()} items")

if __name__ == "__main__":
    seed_database()