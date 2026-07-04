import os
import logging
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from contextlib import contextmanager
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        # Database connection string from environment variables
        # Example: postgresql://user:password@localhost:5432/natiq_db
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable is not set.")

        # Initialize connection pool (min 2, max 10 connections)
        self.pool = pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=10,
            dsn=self.db_url
        )
        
        self._init_tables()
        logger.info("Database Manager initialized.")

    def _init_tables(self):
        """Creates necessary tables if they do not exist."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Cache for verses to reduce API requests
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS cached_verses (
                        ayah_uuid VARCHAR(255) PRIMARY KEY,
                        verse_text TEXT NOT NULL,
                        translation TEXT NOT NULL,
                        surah_name VARCHAR(100),
                        verse_number INTEGER,
                        cached_at TIMESTAMP DEFAULT NOW()
                    );
                """)

                # 2. Bot State to track the last sent verse for sequential logic
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS bot_state (
                        key VARCHAR(50) PRIMARY KEY,
                        value JSONB NOT NULL,
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                """)

                # 3. Rate Limiting: Track requests per chat
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS rate_limits (
                        chat_id BIGINT,
                        request_time TIMESTAMP,
                        PRIMARY KEY (chat_id, request_time)
                    );
                """)

                # 4. Pending Requests: Handle downtime/coalescing
                # If a request is 'pending', it means the bot is processing it.
                # Other requests from the same chat are ignored until this is 'processed'.
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pending_requests (
                        id SERIAL PRIMARY KEY,
                        chat_id BIGINT UNIQUE,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                conn.commit()

    @contextmanager
    def get_connection(self):
        """Context manager to handle database connections safely."""
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            self.pool.putconn(conn)

    def get_connection(self):
        """Returns a connection (used by context manager internally)."""
        return self.pool.getconn()

    # --- Cache Management ---

    def cache_verse(self, verse_data: dict):
        """Stores a verse in the database cache."""
        sql = """
            INSERT INTO cached_verses (ayah_uuid, verse_text, translation, surah_name, verse_number)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (ayah_uuid) DO NOTHING
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (
                    verse_data['uuid'],
                    verse_data['text'],
                    verse_data.get('translation', ''),
                    verse_data.get('surah_name', ''),
                    verse_data.get('verse_number', 0)
                ))

    def get_cached_verse(self, ayah_uuid: str) -> dict:
        """Retrieves a verse from cache."""
        sql = "SELECT * FROM cached_verses WHERE ayah_uuid = %s"
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (ayah_uuid,))
                row = cur.fetchone()
                if row:
                    return dict(row)
        return None

    def clear_cache(self):
        """Clears the entire verse cache (useful for updates)."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE cached_verses")
                logger.info("Verse cache cleared.")

    # --- State Management (Next Verse) ---

    def get_next_verse_uuid(self) -> str:
        """
        Returns the UUID of the next

