import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# loading my .env file
load_dotenv()

# creating SQLAlchemy engine to avoid pandas warning
db_url = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
engine = create_engine(db_url)

# also keeping mysql connector for update operations
try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    print("✅ Connected to MySQL!")
except mysql.connector.Error as e:
    print(f"❌ Connection failed: {e}")
    exit()

# pulling the KPIs I calculated in day 3
df = pd.read_sql("SELECT * FROM product_kpis", engine)
print(f"✅ Loaded KPIs for {len(df)} products")

# using median as the cutoff point for high vs low
revenue_median = df['total_revenue'].median()
growth_median = df['mom_growth_pct'].median()

print(f"\n📊 Revenue Median: ${revenue_median:.2f}")
print(f"📊 Growth Median: {growth_median:.2f}%")

# this function checks each product's revenue and growth
# and decides which BCG category it belongs to
def assign_bcg(row):
    high_revenue = row['total_revenue'] >= revenue_median
    high_growth = row['mom_growth_pct'] > 0
    declining = row['mom_growth_pct'] <= 0

    if high_revenue and high_growth:
        return 'Star'
    elif high_revenue and declining:
        return 'Cash Cow'
    elif not high_revenue and high_growth:
        return 'Hidden Gem'
    elif not high_revenue and declining:
        return 'Dead Weight'
    else:
        return 'Question Mark'

# applying BCG logic to all 1850 products
df['bcg_category'] = df.apply(assign_bcg, axis=1)

# printing final category counts
counts = df['bcg_category'].value_counts()
print("\n📊 BCG Matrix Results:")
print(f"⭐ Stars: {counts.get('Star', 0)}")
print(f"🐄 Cash Cows: {counts.get('Cash Cow', 0)}")
print(f"💎 Hidden Gems: {counts.get('Hidden Gem', 0)}")
print(f"❓ Question Marks: {counts.get('Question Mark', 0)}")
print(f"❌ Dead Weight: {counts.get('Dead Weight', 0)}")

# saving BCG results back to MySQL
cursor = conn.cursor()

# adding bcg_category column - if already exists just update it
try:
    cursor.execute("ALTER TABLE product_kpis ADD COLUMN bcg_category VARCHAR(50)")
except:
    pass

# updating every product's BCG category in MySQL
for _, row in df.iterrows():
    cursor.execute("""
        UPDATE product_kpis 
        SET bcg_category = %s 
        WHERE product_name = %s
    """, (row['bcg_category'], row['product_name']))

conn.commit()
print(f"✅ BCG categories saved to MySQL for all {len(df)} products")

cursor.close()
conn.close()