import time
from typing import Dict, Any
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

class HybridMemoryAgent:
    """
    POC kết hợp Vector Store (lưu episodic memory) và Feature Store (lưu profile).
    Sử dụng Qdrant in-memory và Mock Feature Store dictionary.
    """
    def __init__(self):
        self.embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self.client = QdrantClient(":memory:")
        self.client.create_collection(
            collection_name="episodic_memory",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        self.point_id = 0
        # Mocking Feature Store cho Semantic Profile
        self.feature_store = {}

    def remember(self, text: str, user_id: str):
        # 1. Lưu vào Episodic Memory (Qdrant Vector Store)
        vector = list(self.embedder.embed([text]))[0].tolist()
        self.client.upsert(
            collection_name="episodic_memory",
            points=[PointStruct(
                id=self.point_id, 
                vector=vector, 
                payload={"user_id": user_id, "text": text, "timestamp": time.time()}
            )]
        )
        self.point_id += 1
        
        # 2. Phân tích lưu vào Semantic Profile (Feature Store)
        if user_id not in self.feature_store:
            self.feature_store[user_id] = {"preferences": [], "last_seen": time.time()}
        
        lower_text = text.lower()
        if any(keyword in lower_text for keyword in ["thích", "ghét", "tên là"]):
            self.feature_store[user_id]["preferences"].append(text)
        self.feature_store[user_id]["last_seen"] = time.time()

    def recall(self, query: str, user_id: str) -> Dict[str, Any]:
        vector = list(self.embedder.embed([query]))[0].tolist()
        
        # 1. Trích xuất từ Episodic Memory (lọc theo user_id)
        results = self.client.search(
            collection_name="episodic_memory",
            query_vector=vector,
            query_filter=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
            ),
            limit=3
        )
        episodes = [hit.payload["text"] for hit in results if hit.score > 0.4]
        
        # 2. Trích xuất từ Profile (Feature Store)
        profile = self.feature_store.get(user_id, {"preferences": []})
        
        return {
            "query": query,
            "user_profile": profile["preferences"],
            "relevant_episodes": episodes
        }
