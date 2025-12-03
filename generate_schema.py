"""
Script to generate schema.txt from netcaredb_ai database
No langchain dependency required
"""

import mysql.connector

# ============ Database Connection Info ============
config = {
    'host': '172.31.26.206',
    'port': 3306,
    'user': 'ai_test',
    'password': 'Netcare@13579',
    'database': 'netcaredb_ai'
}

OUTPUT_FILE = 'schema_netcare.txt'

print(f"Connecting to {config['host']}:{config['port']}/{config['database']}...")

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("Connected successfully!")
except Exception as e:
    print(f"Connection failed: {e}")
    exit(1)

# Get all tables
cursor.execute("SHOW TABLES")
tables = [row[0] for row in cursor.fetchall()]
print(f"Found {len(tables)} tables")

schema_content = ""

for table in tables:
    print(f"Processing table: {table}")
    
    # Get CREATE TABLE statement
    cursor.execute(f"SHOW CREATE TABLE `{table}`")
    create_stmt = cursor.fetchone()[1]
    
    # Get sample data (3 rows)
    cursor.execute(f"SELECT * FROM `{table}` LIMIT 3")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    # Build schema content
    schema_content += f"\n{create_stmt}\n\n"
    schema_content += f"/*\n3 rows from {table} table:\n"
    schema_content += "\t".join(columns) + "\n"
    for row in rows:
        schema_content += "\t".join([str(val) if val is not None else 'None' for val in row]) + "\n"
    schema_content += "*/\n\n"

# Save to file
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write(schema_content)

cursor.close()
conn.close()

print(f"\nSchema saved to: {OUTPUT_FILE}")
print("Done!")