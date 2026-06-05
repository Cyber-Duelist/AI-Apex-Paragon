import sqlite3
import os

print("=== 1. INITIALIZING DATABASE ===")
# Ensure the folder exists before trying to create the file inside it
os.makedirs("week_05/sql_fastapi", exist_ok=True)

# Connect to the database (this physically creates 'documents.db' if it doesn't exist)
db_path = "week_05/sql_fastapi/documents.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# We drop the table if it already exists so that if you run this script twice, 
# you don't end up with 20 rows, then 30 rows, etc.
cursor.execute("DROP TABLE IF EXISTS documents")

print("=== 2. CREATING TABLE ===")
# Here we define the exact columns and what type of data they are allowed to hold
cursor.execute("""
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    department TEXT,
    num_pages INTEGER,
    high_risk INTEGER,
    created_at TEXT
)
""")

print("=== 3. INSERTING 10 SAMPLE RECORDS ===")
# We create a list of 10 fake documents with different risk levels and departments
sample_data = [
    ('Contract A', 'Legal', 12, 1, '2024-01-10'),
    ('Employee Handbook', 'HR', 45, 0, '2024-01-12'),
    ('Q1 Financials', 'Finance', 23, 0, '2024-01-15'),
    ('Merger Agreement', 'Legal', 105, 1, '2024-01-18'),
    ('Tax Audit 2023', 'Finance', 34, 1, '2024-01-20'),
    ('Offer Letter - John', 'HR', 3, 0, '2024-01-22'),
    ('Vendor NDA', 'Legal', 8, 0, '2024-01-25'),
    ('Compliance Violation', 'HR', 5, 1, '2024-01-28'),
    ('Payroll Export', 'Finance', 120, 0, '2024-02-01'),
    ('Litigation Notice', 'Legal', 14, 1, '2024-02-05')
]

# executemany is a fast way to insert a massive list of data all at once
cursor.executemany("""
INSERT INTO documents (title, department, num_pages, high_risk, created_at)
VALUES (?, ?, ?, ?, ?)
""", sample_data)

# Commit acts as the "Save" button to lock the data into the hard drive
conn.commit()


print("\n=== ALL DOCUMENTS ===")
# Query 1: Give me absolutely everything in the table
cursor.execute("SELECT * FROM documents")
for row in cursor.fetchall():
    print(row)

print("\n=== HIGH RISK DOCUMENTS ===")
# Query 2: Filter the data directly in SQL (Much faster than filtering in Python!)
cursor.execute("SELECT * FROM documents WHERE high_risk = 1")
for row in cursor.fetchall():
    print(row)

print("\n=== DOCUMENTS PER DEPARTMENT ===")
# Query 3: Group the data and count it
cursor.execute("SELECT department, COUNT(*) FROM documents GROUP BY department")
for row in cursor.fetchall():
    print(row)

# Always close the connection to prevent memory leaks
cursor.close()
conn.close()