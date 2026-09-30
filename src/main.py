import time
from dotenv import load_dotenv

# loading my .env file so all scripts can access database credentials
load_dotenv()

print("=" * 50)
print("🚀 ProductIQ Pipeline Starting...")
print("=" * 50)

start_time = time.time()

# step 1 - first calculate KPIs for all 1850 products
print("\n📊 Step 1: Calculating Product KPIs...")
import kpi_calculator
print("✅ KPIs calculated successfully!")

# step 2 - now run BCG matrix to categorize each product
print("\n📊 Step 2: Running BCG Matrix Algorithm...")
import bcg_matrix
print("✅ BCG Matrix complete!")

# step 3 - send BCG results to Gemini AI and get recommendations
print("\n🤖 Step 3: Generating AI Recommendations...")
import ai_strategist
print("✅ AI Recommendations generated!")

# checking how long the full pipeline took to run
end_time = time.time()
total_time = round(end_time - start_time, 2)

print("\n" + "=" * 50)
print("✅ ProductIQ Pipeline Complete!")
print(f"⏱️  Total time: {total_time} seconds")
print("=" * 50)