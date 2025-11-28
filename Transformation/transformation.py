import pandas as pd
import os

# Create output directory for dimension and fact tables
output_dir = "Transformed"
os.makedirs(output_dir, exist_ok=True)

# Load the cleansed data
df = pd.read_csv("../train_cleansed.csv")

# Parse dates
df['Order Date'] = pd.to_datetime(df['Order Date'], format='mixed', dayfirst=True, errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='mixed', dayfirst=True, errors='coerce')

print(f"Loaded {len(df)} rows from train_cleansed.csv")

####################################################
# DIMENSION TABLES
####################################################

# Dim_Time - Extract unique dates from both Order Date and Ship Date
print("\nCreating Dim_Time...")
all_dates = pd.concat([df['Order Date'], df['Ship Date']]).dropna().unique()
all_dates = pd.to_datetime(all_dates)

dim_time = pd.DataFrame({
    'date': sorted(all_dates)
})

dim_time['time_key'] = range(1, len(dim_time) + 1)
dim_time['year'] = dim_time['date'].dt.year
dim_time['quarter'] = 'Q' + dim_time['date'].dt.quarter.astype(str)
dim_time['month'] = dim_time['date'].dt.month
dim_time['month_name'] = dim_time['date'].dt.month_name()
dim_time['week'] = dim_time['date'].dt.isocalendar().week
dim_time['day'] = dim_time['date'].dt.day
dim_time['day_of_week'] = dim_time['date'].dt.dayofweek
dim_time['day_of_year'] = dim_time['date'].dt.dayofyear

# Reorder columns
dim_time = dim_time[['time_key', 'date', 'year', 'quarter', 'month', 'month_name', 
                     'week', 'day', 'day_of_week', 'day_of_year']]

dim_time.to_csv(f"{output_dir}/dim_time.csv", index=False)
print(f"Created Dim_Time with {len(dim_time)} rows")

# Dim_Customer - Unique customers with their attributes
print("\nCreating Dim_Customer...")
dim_customer = df[['Customer ID', 'Customer Name', 'Segment', 'Country', 
                   'City', 'State', 'Postal Code', 'Region']].drop_duplicates(subset='Customer ID')

dim_customer['customer_key'] = range(1, len(dim_customer) + 1)
dim_customer = dim_customer.rename(columns={
    'Customer ID': 'customer_id',
    'Customer Name': 'customer_name',
    'Segment': 'segment',
    'Country': 'country',
    'City': 'city',
    'State': 'state',
    'Postal Code': 'postal_code',
    'Region': 'region'
})

# Reorder columns
dim_customer = dim_customer[['customer_key', 'customer_id', 'customer_name', 'segment',
                             'country', 'city', 'state', 'postal_code', 'region']]

dim_customer.to_csv(f"{output_dir}/dim_customer.csv", index=False)
print(f"Created Dim_Customer with {len(dim_customer)} rows")

# Dim_Product - Unique products with their attributes
print("\nCreating Dim_Product...")
dim_product = df[['Product ID', 'Product Name', 'Category', 'Sub-Category']].drop_duplicates(subset='Product ID')

dim_product['product_key'] = range(1, len(dim_product) + 1)
dim_product = dim_product.rename(columns={
    'Product ID': 'product_id',
    'Product Name': 'product_name',
    'Category': 'category',
    'Sub-Category': 'sub_category'
})

# Reorder columns
dim_product = dim_product[['product_key', 'product_id', 'product_name', 'category', 'sub_category']]

dim_product.to_csv(f"{output_dir}/dim_product.csv", index=False)
print(f"Created Dim_Product with {len(dim_product)} rows")

# Dim_Shipment - Unique shipment modes and dates
print("\nCreating Dim_Shipment...")
dim_shipment = df[['Ship Mode', 'Ship Date']].drop_duplicates()

dim_shipment['ship_key'] = range(1, len(dim_shipment) + 1)
dim_shipment = dim_shipment.rename(columns={
    'Ship Mode': 'ship_mode',
    'Ship Date': 'ship_date'
})

# Reorder columns
dim_shipment = dim_shipment[['ship_key', 'ship_mode', 'ship_date']]

dim_shipment.to_csv(f"{output_dir}/dim_shipment.csv", index=False)
print(f"Created Dim_Shipment with {len(dim_shipment)} rows")

# Dim_Order - Unique orders with order dates
print("\nCreating Dim_Order...")
dim_order = df[['Order ID', 'Order Date']].drop_duplicates(subset='Order ID')

dim_order['order_key'] = range(1, len(dim_order) + 1)
dim_order = dim_order.rename(columns={
    'Order ID': 'order_id',
    'Order Date': 'order_date'
})

# Reorder columns
dim_order = dim_order[['order_key', 'order_id', 'order_date']]

dim_order.to_csv(f"{output_dir}/dim_order.csv", index=False)
print(f"Created Dim_Order with {len(dim_order)} rows")

####################################################
# FACT TABLE
####################################################

print("\nCreating Fact_Sales...")

# Create fact table by merging with dimension tables to get surrogate keys
fact_sales = df[['Row ID', 'Order ID', 'Customer ID', 'Product ID', 
                 'Ship Mode', 'Ship Date', 'Order Date', 'Sales']].copy()

# Merge with dimension tables to get surrogate keys
fact_sales = fact_sales.merge(
    dim_order[['order_key', 'order_id']], 
    left_on='Order ID', 
    right_on='order_id', 
    how='left'
).drop('order_id', axis=1)

fact_sales = fact_sales.merge(
    dim_customer[['customer_key', 'customer_id']], 
    left_on='Customer ID', 
    right_on='customer_id', 
    how='left'
).drop('customer_id', axis=1)

fact_sales = fact_sales.merge(
    dim_product[['product_key', 'product_id']], 
    left_on='Product ID', 
    right_on='product_id', 
    how='left'
).drop('product_id', axis=1)

fact_sales = fact_sales.merge(
    dim_shipment[['ship_key', 'ship_mode', 'ship_date']], 
    left_on=['Ship Mode', 'Ship Date'], 
    right_on=['ship_mode', 'ship_date'], 
    how='left'
).drop(['ship_mode', 'ship_date'], axis=1)

# Merge with time dimension based on Order Date
fact_sales = fact_sales.merge(
    dim_time[['time_key', 'date']], 
    left_on='Order Date', 
    right_on='date', 
    how='left'
).drop('date', axis=1)

# Rename and select final columns
fact_sales = fact_sales.rename(columns={
    'Row ID': 'row_id',
    'Sales': 'sales'
})

# Select and reorder final columns for fact table
fact_sales = fact_sales[['row_id', 'order_key', 'customer_key', 'product_key', 
                         'ship_key', 'time_key', 'sales']]

# Remove any rows with missing keys (shouldn't happen but safety check)
initial_rows = len(fact_sales)
fact_sales = fact_sales.dropna()
final_rows = len(fact_sales)

if initial_rows != final_rows:
    print(f"Warning: Removed {initial_rows - final_rows} rows with missing keys")

fact_sales.to_csv(f"{output_dir}/fact_sales.csv", index=False)
print(f"Created Fact_Sales with {len(fact_sales)} rows")

####################################################
# SUMMARY
####################################################

print("\n" + "="*60)
print("TRANSFORMATION COMPLETE")
print("="*60)
print(f"\nDimension Tables:")
print(f"  - dim_time.csv: {len(dim_time)} rows")
print(f"  - dim_customer.csv: {len(dim_customer)} rows")
print(f"  - dim_product.csv: {len(dim_product)} rows")
print(f"  - dim_shipment.csv: {len(dim_shipment)} rows")
print(f"  - dim_order.csv: {len(dim_order)} rows")
print(f"\nFact Table:")
print(f"  - fact_sales.csv: {len(fact_sales)} rows")
print(f"\nAll files saved to: {output_dir}/")
print("="*60)
