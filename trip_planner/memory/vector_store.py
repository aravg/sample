import os
import json
import pickle
from typing import List, Dict, Any, Optional
from config import VECTOR_STORE_PATH


class VectorMemory:
    """FAISS-based vector memory for semantic retrieval of past trip preferences."""

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.store_path = os.path.join(VECTOR_STORE_PATH, f"{user_id}")
        os.makedirs(self.store_path, exist_ok=True)
        self._embeddings = None
        self._index = None
        self._documents: List[Dict] = []
        self._load()

    def _get_embeddings(self):
        if self._embeddings is None:
            try:
                from langchain_anthropic import ChatAnthropic
                from langchain_community.embeddings import FakeEmbeddings
                from config import ANTHROPIC_API_KEY, OPENAI_API_KEY
                if OPENAI_API_KEY:
                    from langchain_openai import OpenAIEmbeddings
                    self._embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
                else:
                    self._embeddings = FakeEmbeddings(size=384)
            except Exception:
                from langchain_community.embeddings import FakeEmbeddings
                self._embeddings = FakeEmbeddings(size=384)
        return self._embeddings

    def add_memory(self, content: str, metadata: Dict[str, Any]) -> None:
        """Store a memory document."""
        doc = {"content": content, "metadata": metadata}
        self._documents.append(doc)
        self._save()

    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve k most relevant memories (simplified keyword search)."""
        if not self._documents:
            return []
        query_lower = query.lower()
        scored = []
        for doc in self._documents:
            score = sum(
                1 for word in query_lower.split()
                if word in doc["content"].lower()
            )
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: -x[0])
        return [d for _, d in scored[:k]]

    def get_user_preferences(self) -> Dict[str, Any]:
        """Extract aggregated preferences from memory."""
        if not self._documents:
            return {}
        prefs = {
            "past_destinations": [],
            "preferred_hotel_type": None,
            "preferred_travel_type": None,
            "avg_budget": None,
        }
        budgets = []
        for doc in self._documents:
            meta = doc.get("metadata", {})
            if dest := meta.get("destination"):
                prefs["past_destinations"].append(dest)
            if budget := meta.get("budget"):
                try:
                    budgets.append(float(budget))
                except (ValueError, TypeError):
                    pass
            if hotel := meta.get("hotel_preference"):
                prefs["preferred_hotel_type"] = hotel
            if travel_type := meta.get("travel_type"):
                prefs["preferred_travel_type"] = travel_type
        if budgets:
            prefs["avg_budget"] = sum(budgets) / len(budgets)
        return prefs

    def _save(self) -> None:
        docs_path = os.path.join(self.store_path, "documents.json")
        with open(docs_path, "w") as f:
            json.dump(self._documents, f, indent=2)

    def _load(self) -> None:
        docs_path = os.path.join(self.store_path, "documents.json")
        if os.path.exists(docs_path):
            with open(docs_path) as f:
                self._documents = json.load(f)
