import sqlite3

# Connect to the database we built in Pack 1
db_path = "week_05/sql_fastapi/documents.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Q1: MORE THAN 20 PAGES ===")
# WHERE allows us to filter based on numerical thresholds
cursor.execute("SELECT * FROM documents WHERE num_pages > 20")
for row in cursor.fetchall():
    print(row)

print("\n=== Q2: HIGH RISK + LEGAL ===")
# AND allows us to chain multiple conditions together
cursor.execute("SELECT * FROM documents WHERE high_risk = 1 AND department = 'Legal'")
for row in cursor.fetchall():
    print(row)

print("\n=== Q3: SORTED BY PAGES DESC ===")
# ORDER BY DESC sorts from largest to smallest
cursor.execute("SELECT * FROM documents ORDER BY num_pages DESC")
for row in cursor.fetchall():
    print(row)

print("\n=== Q4: AVG PAGES PER DEPARTMENT ===")
# AVG() calculates the average, and GROUP BY splits it by category
cursor.execute("SELECT department, AVG(num_pages) FROM documents GROUP BY department")
for row in cursor.fetchall():
    # We round the average to 2 decimal places for cleaner output
    print((row[0], round(row[1], 2)))

print("\n=== Q5: HIGH RISK COUNT PER DEPARTMENT ===")
# We filter FOR high risk first, THEN group them up and count them
cursor.execute("SELECT department, COUNT(*) FROM documents WHERE high_risk = 1 GROUP BY department")
for row in cursor.fetchall():
    print(row)

print("\n=== Q6: TOP 3 LARGEST DOCUMENTS ===")
# LIMIT chops off the results after a certain number. This is how "Top 10" lists work!
cursor.execute("SELECT * FROM documents ORDER BY num_pages DESC LIMIT 3")
for row in cursor.fetchall():
    print(row)

# Always close the connection
cursor.close()
conn.close()