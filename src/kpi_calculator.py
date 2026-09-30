import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import mysql.connector

# loading my .env file
load_dotenv()

# creating SQLAlchemy engine to avoid pandas warning
db_url = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
engine = create_engine(db_url)

# also keeping mysql connector for insert operations
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

# pulling all sales data using SQLAlchemy engine
df = pd.read_sql("SELECT * FROM superstore", engine)
print(f"✅ Loaded {len(df)} rows from MySQL")

# converting order_date to datetime so I can extract year
df['order_date'] = pd.to_datetime(df['order_date'])
df['year'] = df['order_date'].dt.year

# calculating main KPIs for each product
product_kpis = df.groupby('product_name').agg(
    total_revenue=('sales', 'sum'),
    total_profit=('profit', 'sum'),
    quantity_sold=('quantity', 'sum'),
    total_orders=('order_id', 'count')
).reset_index()

# profit margin % = (profit / revenue) * 100
product_kpis['profit_margin_pct'] = (
    product_kpis['total_profit'] / product_kpis['total_revenue'] * 100
).round(2)

# calculating yearly growth - comparing 2017 vs 2016 revenue per product
rev_2017 = df[df['year'] == 2017].groupby('product_name')['sales'].sum()
rev_2016 = df[df['year'] == 2016].groupby('product_name')['sales'].sum()

# growth % = ((2017 revenue - 2016 revenue) / 2016 revenue) * 100
growth = ((rev_2017 - rev_2016) / rev_2016 * 100).round(2)
growth.name = 'mom_growth_pct'

# merging growth into main KPI table
product_kpis = product_kpis.merge(growth, on='product_name', how='left')

# filling null growth with 0 for products that didn't sell in both years
product_kpis['mom_growth_pct'] = product_kpis['mom_growth_pct'].fillna(0)

print(f"✅ KPIs calculated for {len(product_kpis)} products")

# saving KPI results back to MySQL
cursor = conn.cursor()

# dropping table if exists so we start fresh every time
cursor.execute("DROP TABLE IF EXISTS product_kpis")
cursor.execute("""
    CREATE TABLE product_kpis (
        product_name VARCHAR(255),
        total_revenue DECIMAL(10,2),
        total_profit DECIMAL(10,2),
        quantity_sold INT,
        total_orders INT,
        profit_margin_pct DECIMAL(10,2),
        mom_growth_pct DECIMAL(10,2)
    )
""")

# inserting each product's KPIs into MySQL
for _, row in product_kpis.iterrows():
    cursor.execute("""
        INSERT INTO product_kpis VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, tuple(row))

conn.commit()
print(f"✅ Saved {len(product_kpis)} products to product_kpis table in MySQL")

cursor.close()
conn.close()