"""
ComplianceAI - SQLite Database Module
Handles all database operations for users, documents, analyses, tickets, and usage tracking.
"""

import sqlite3
import os
import json
from datetime import datetime


DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "complianceai.db")


def _get_connection():
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they do not exist."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            email TEXT,
            password_hash TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            filename TEXT,
            page_count INTEGER,
            chunk_count INTEGER,
            status TEXT DEFAULT 'uploaded',
            upload_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY,
            document_id INTEGER,
            user_id INTEGER,
            framework TEXT,
            risk_score REAL,
            risk_level TEXT,
            findings TEXT,
            recommendations TEXT,
            created_at TEXT,
            FOREIGN KEY (document_id) REFERENCES documents(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY,
            analysis_id INTEGER,
            user_id INTEGER,
            title TEXT,
            priority TEXT,
            status TEXT DEFAULT 'open',
            created_at TEXT,
            FOREIGN KEY (analysis_id) REFERENCES analyses(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            query_date TEXT,
            query_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# User operations
# ---------------------------------------------------------------------------

def create_user(username, email, password_hash):
    """Create a new user and return the user id."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (username, email, password_hash, datetime.now().isoformat()),
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id


def get_user(username):
    """Return a user dict by username, or None if not found."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


# ---------------------------------------------------------------------------
# Document operations
# ---------------------------------------------------------------------------

def add_document(user_id, filename, page_count, chunk_count):
    """Add a document record and return its id."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (user_id, filename, page_count, chunk_count, status, upload_date) "
        "VALUES (?, ?, ?, ?, 'uploaded', ?)",
        (user_id, filename, page_count, chunk_count, datetime.now().isoformat()),
    )
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doc_id


def get_user_documents(user_id):
    """Return a list of document dicts for a given user."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM documents WHERE user_id = ? ORDER BY upload_date DESC",
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_document(doc_id, user_id):
    """Delete a document belonging to the specified user."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM documents WHERE id = ? AND user_id = ?",
        (doc_id, user_id),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Analysis operations
# ---------------------------------------------------------------------------

def add_analysis(document_id, user_id, framework, risk_score, risk_level, findings_json, recommendations):
    """Add an analysis record and return its id.

    Parameters
    ----------
    findings_json : str | list | dict
        If a list or dict is passed it will be serialised to a JSON string
        automatically.
    """
    if not isinstance(findings_json, str):
        findings_json = json.dumps(findings_json)

    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO analyses (document_id, user_id, framework, risk_score, risk_level, findings, recommendations, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (document_id, user_id, framework, risk_score, risk_level, findings_json, recommendations, datetime.now().isoformat()),
    )
    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analysis_id


def get_document_analyses(document_id):
    """Return all analyses for a given document."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM analyses WHERE document_id = ? ORDER BY created_at DESC",
        (document_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        try:
            d["findings"] = json.loads(d["findings"])
        except (json.JSONDecodeError, TypeError):
            pass
        results.append(d)
    return results


def get_user_analyses(user_id):
    """Return all analyses for a given user."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM analyses WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    results = []
    for r in rows:
        d = dict(r)
        try:
            d["findings"] = json.loads(d["findings"])
        except (json.JSONDecodeError, TypeError):
            pass
        results.append(d)
    return results


# ---------------------------------------------------------------------------
# Ticket operations
# ---------------------------------------------------------------------------

def add_ticket(analysis_id, user_id, title, priority):
    """Add a ticket and return its id."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tickets (analysis_id, user_id, title, priority, status, created_at) "
        "VALUES (?, ?, ?, ?, 'open', ?)",
        (analysis_id, user_id, title, priority, datetime.now().isoformat()),
    )
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ticket_id


def get_user_tickets(user_id):
    """Return all tickets for a given user."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM tickets WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_ticket_status(ticket_id, status):
    """Update the status of a ticket."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tickets SET status = ? WHERE id = ?",
        (status, ticket_id),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Usage / rate-limiting
# ---------------------------------------------------------------------------

def check_rate_limit(user_id, daily_limit=20):
    """Return True if the user is still under the daily query limit."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT query_count FROM usage WHERE user_id = ? AND query_date = ?",
        (user_id, today),
    )
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return True
    return row["query_count"] < daily_limit


def increment_usage(user_id):
    """Increment the daily query count for the user."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, query_count FROM usage WHERE user_id = ? AND query_date = ?",
        (user_id, today),
    )
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            "INSERT INTO usage (user_id, query_date, query_count) VALUES (?, ?, 1)",
            (user_id, today),
        )
    else:
        cursor.execute(
            "UPDATE usage SET query_count = query_count + 1 WHERE id = ?",
            (row["id"],),
        )

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def get_user_stats(user_id):
    """Return aggregate stats for a user.

    Returns
    -------
    dict
        Keys: total_docs, total_analyses, avg_risk, open_tickets
    """
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS cnt FROM documents WHERE user_id = ?", (user_id,))
    total_docs = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM analyses WHERE user_id = ?", (user_id,))
    total_analyses = cursor.fetchone()["cnt"]

    cursor.execute("SELECT AVG(risk_score) AS avg_risk FROM analyses WHERE user_id = ?", (user_id,))
    avg_risk_row = cursor.fetchone()
    avg_risk = round(avg_risk_row["avg_risk"], 2) if avg_risk_row["avg_risk"] is not None else 0.0

    cursor.execute(
        "SELECT COUNT(*) AS cnt FROM tickets WHERE user_id = ? AND status = 'open'",
        (user_id,),
    )
    open_tickets = cursor.fetchone()["cnt"]

    conn.close()
    return {
        "total_docs": total_docs,
        "total_analyses": total_analyses,
        "avg_risk": avg_risk,
        "open_tickets": open_tickets,
    }
