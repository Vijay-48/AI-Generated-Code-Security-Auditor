<<<<<<< HEAD
from app.services.rag_service import RAGRemediationService

def seed_database():
    rag = RAGRemediationService()
    print(f"Database seeded with {rag.col.count()} items")

if __name__ == "__main__":
=======
from app.services.rag_service import RAGRemediationService

def seed_database():
    rag = RAGRemediationService()
    print(f"Database seeded with {rag.col.count()} items")

if __name__ == "__main__":
>>>>>>> 6beaaa9d992e786be91fc4cc04bf2dff00a41321
    seed_database()