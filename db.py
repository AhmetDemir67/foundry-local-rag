import json
import sqlite3

from config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_table(baglanti):
    baglanti.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    """)


def clear_chunks(baglanti):
    baglanti.execute("DELETE FROM chunks")


def insert_chunk(baglanti, source, content, embedding):
    baglanti.execute(
        "INSERT INTO chunks (source, content, embedding) VALUES (?, ?, ?)",
        (source, content, json.dumps(embedding)),
    )


def fetch_all_chunks(baglanti):
    satirlar = baglanti.execute("SELECT source, content, embedding FROM chunks").fetchall()
    return [(source, content, json.loads(embedding)) for source, content, embedding in satirlar]
