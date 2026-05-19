import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from config import DB_PATH


class SessionStore:
    """In-memory session store (Redis-compatible interface)."""

    def __init__(self):
        self._store: Dict[str, Any] = {}

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        self._store[key] = {
            "value": value,
            "expires_at": datetime.now().timestamp() + ttl,
        }

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        if datetime.now().timestamp() > item["expires_at"]:
            del self._store[key]
            return None
        return item["value"]

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


class TripDatabase:
    """SQLite-based persistent storage for trip history (PostgreSQL-compatible interface)."""

    def __init__(self):
        self._init_db()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    source TEXT NOT NULL,
                    travel_dates TEXT,
                    budget REAL,
                    travelers INTEGER,
                    travel_type TEXT,
                    plan_json TEXT,
                    pdf_path TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    preferences_json TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(DB_PATH)

    def save_trip(self, user_id: str, trip_data: Dict[str, Any]) -> int:
        prefs = trip_data.get("trip_preferences", {})
        with self._conn() as conn:
            cursor = conn.execute(
                """INSERT INTO trips
                   (user_id, destination, source, travel_dates, budget,
                    travelers, travel_type, plan_json, pdf_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    user_id,
                    prefs.get("destination", ""),
                    prefs.get("source", ""),
                    json.dumps(prefs.get("dates", {})),
                    prefs.get("budget", 0),
                    prefs.get("travelers", 1),
                    prefs.get("travel_type", ""),
                    json.dumps(trip_data.get("final_plan", {})),
                    trip_data.get("pdf_path", ""),
                ),
            )
            return cursor.lastrowid

    def get_user_trips(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM trips WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        trips = []
        cols = ["id", "user_id", "destination", "source", "travel_dates",
                "budget", "travelers", "travel_type", "plan_json", "pdf_path", "created_at"]
        for row in rows:
            d = dict(zip(cols, row))
            d["plan"] = json.loads(d.pop("plan_json", "{}") or "{}")
            trips.append(d)
        return trips

    def save_user_profile(self, user_id: str, name: str, email: str, preferences: Dict) -> None:
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO user_profiles
                   (user_id, name, email, preferences_json, updated_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, name, email, json.dumps(preferences), datetime.now().isoformat()),
            )

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM user_profiles WHERE user_id=?", (user_id,)
            ).fetchone()
        if not row:
            return None
        cols = ["user_id", "name", "email", "preferences_json", "updated_at"]
        d = dict(zip(cols, row))
        d["preferences"] = json.loads(d.pop("preferences_json", "{}") or "{}")
        return d
