import pandas as pd

# reading the data - using latin-1 because 
# some customer names have special characters
df = pd.read_csv("data/Sample - Superstore.csv", encoding= "latin-1")

print(f"rows: {len(df)}")
print(f"columns: {len(df.columns)}")

# checking all column names before i start analysis
# want to know exactly what data i have
for i, col in enumerate(df.columns, 1):
    print(f"{i}. {col}")

# looking at first few rows to understand structure
print(df.head(3).to_string())

# basic numbers to understand scale of business
# 1862 products across 3 categories - good variety
print(f"unique products: {df['Product Name'].nunique()}")
print(f"unique customers: {df['Customer Name'].nunique()}")
print(f"regions: {df['Region'].unique()}")
print(f"categories: {df['Category'].unique()}")

# total revenue and profit - understanding 
# overall business health before deep dive
print(f"total sales: ${df['Sales'].sum():,.2f}")
print(f"total profit: ${df['Profit'].sum():,.2f}")