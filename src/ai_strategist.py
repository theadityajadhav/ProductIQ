import mysql.connector
from google import genai
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import time

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

# setting up Gemini AI with my API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
print("✅ Gemini AI ready!")

# pulling BCG results from MySQL using SQLAlchemy
df = pd.read_sql("SELECT * FROM product_kpis", engine)
print(f"✅ Loaded {len(df)} products from MySQL")

# grouping products by BCG category to send each group to Gemini
category_summary = df.groupby('bcg_category').agg(
    total_products=('product_name', 'count'),
    avg_revenue=('total_revenue', 'mean'),
    avg_profit=('profit_margin_pct', 'mean'),
    avg_growth=('mom_growth_pct', 'mean')
).reset_index()

# this function sends category data to Gemini and gets back a recommendation
# retries automatically if rate limit hits
def get_ai_recommendation(category, total_products, avg_revenue, avg_profit, avg_growth):
    prompt = f"""
    You are a business strategy consultant analyzing e-commerce product performance.
    
    BCG Category: {category}
    Number of Products: {total_products}
    Average Revenue per Product: ${avg_revenue:.2f}
    Average Profit Margin: {avg_profit:.2f}%
    Average Growth Rate: {avg_growth:.2f}%
    
    Give a specific, actionable business recommendation in 2-3 sentences.
    Be direct and practical like a McKinsey consultant would be.
    """
    
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                wait_time = 30 * (attempt + 1)
                print(f"⏳ Rate limit hit. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e
    
    return "Unable to generate recommendation due to API rate limits."

# creating table to store AI recommendations
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS ai_recommendations")
cursor.execute("""
    CREATE TABLE ai_recommendations (
        bcg_category VARCHAR(50),
        total_products INT,
        avg_revenue DECIMAL(10,2),
        avg_profit_margin DECIMAL(10,2),
        avg_growth DECIMAL(10,2),
        ai_recommendation TEXT
    )
""")

# sending each BCG category to Gemini and saving recommendation
print("\n🤖 AI Recommendations:\n")
for _, row in category_summary.iterrows():
    recommendation = get_ai_recommendation(
        row['bcg_category'],
        row['total_products'],
        row['avg_revenue'],
        row['avg_profit'],
        row['avg_growth']
    )
    
    print(f"📌 {row['bcg_category']} ({row['total_products']} products)")
    print(f"💡 {recommendation}")
    print()
    
    # saving to MySQL
    cursor.execute("""
        INSERT INTO ai_recommendations VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        row['bcg_category'],
        int(row['total_products']),
        float(row['avg_revenue']),
        float(row['avg_profit']),
        float(row['avg_growth']),
        recommendation
    ))
    
    # small delay between requests
    time.sleep(5)

conn.commit()
print("✅ All AI recommendations saved to MySQL!")

cursor.close()
conn.close()
print("✅ Done. Connection closed.")