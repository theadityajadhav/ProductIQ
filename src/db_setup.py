import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import os

# loading my database credentials from .env file
load_dotenv()

# connecting to my productiq database using credentials from .env
try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    print("✅ Connected to MySQL successfully!")
except mysql.connector.Error as e:
    print(f"❌ Connection failed: {e}")
    exit()

cursor = conn.cursor()

# just checking how many rows are in my superstore table
cursor.execute("SELECT COUNT(*) FROM superstore")
count = cursor.fetchone()[0]
print(f"✅ Total rows in database: {count}")

# pulling first 5 rows to make sure data looks correct
cursor.execute("SELECT order_id, customer_name, sales, profit FROM superstore LIMIT 5")
rows = cursor.fetchall()
print("\n📊 Sample Data:")
for row in rows:
    print(row)

cursor.close()
conn.close()
print("\n✅ Done. Connection closed.")