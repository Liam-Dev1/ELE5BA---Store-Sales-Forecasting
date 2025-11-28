-- ====================================================
-- Superstore Analytics - Star Schema for Supabase
-- ====================================================

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_time CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_shipment CASCADE;
DROP TABLE IF EXISTS dim_order CASCADE;

-- ====================================================
-- DIMENSION TABLES
-- ====================================================

-- Dim_Time: Temporal dimension with date attributes
CREATE TABLE dim_time (
    time_key INT PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    year INT,
    quarter VARCHAR(10),
    month INT,
    month_name VARCHAR(20),
    week INT,
    day INT,
    day_of_week INT,
    day_of_year INT
);

-- Dim_Customer: Customer dimension with location and segment
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(255),
    segment VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(50)
);

-- Dim_Product: Product dimension with category hierarchy
CREATE TABLE dim_product (
    product_key INT PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_name VARCHAR(255),
    category VARCHAR(100),
    sub_category VARCHAR(100)
);

-- Dim_Shipment: Shipment dimension with mode and date
CREATE TABLE dim_shipment (
    ship_key INT PRIMARY KEY,
    ship_mode VARCHAR(50),
    ship_date DATE
);

-- Dim_Order: Order dimension with order date
CREATE TABLE dim_order (
    order_key INT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL UNIQUE,
    order_date DATE
);

-- ====================================================
-- FACT TABLE
-- ====================================================

-- Fact_Sales: Sales fact table with foreign keys to dimensions
CREATE TABLE fact_sales (
    row_id INT PRIMARY KEY,
    order_key INT NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    ship_key INT NOT NULL,
    time_key INT NOT NULL,
    sales DECIMAL(10, 2) NOT NULL,
    
    -- Foreign key constraints
    CONSTRAINT fk_order FOREIGN KEY (order_key) REFERENCES dim_order(order_key),
    CONSTRAINT fk_customer FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    CONSTRAINT fk_product FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    CONSTRAINT fk_shipment FOREIGN KEY (ship_key) REFERENCES dim_shipment(ship_key),
    CONSTRAINT fk_time FOREIGN KEY (time_key) REFERENCES dim_time(time_key)
);

-- ====================================================
-- INDEXES FOR PERFORMANCE
-- ====================================================

-- Indexes on dimension natural keys
CREATE INDEX idx_customer_id ON dim_customer(customer_id);
CREATE INDEX idx_product_id ON dim_product(product_id);
CREATE INDEX idx_order_id ON dim_order(order_id);
CREATE INDEX idx_time_date ON dim_time(date);

-- Indexes on fact table foreign keys
CREATE INDEX idx_fact_order ON fact_sales(order_key);
CREATE INDEX idx_fact_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_product ON fact_sales(product_key);
CREATE INDEX idx_fact_shipment ON fact_sales(ship_key);
CREATE INDEX idx_fact_time ON fact_sales(time_key);

-- Composite indexes for common queries
CREATE INDEX idx_time_year_month ON dim_time(year, month);
CREATE INDEX idx_customer_region ON dim_customer(region);
CREATE INDEX idx_product_category ON dim_product(category, sub_category);

-- ====================================================
-- COMMENTS
-- ====================================================

COMMENT ON TABLE dim_time IS 'Time dimension containing unique dates and temporal attributes';
COMMENT ON TABLE dim_customer IS 'Customer dimension with demographic and geographic information';
COMMENT ON TABLE dim_product IS 'Product dimension with product hierarchy';
COMMENT ON TABLE dim_shipment IS 'Shipment dimension with shipping details';
COMMENT ON TABLE dim_order IS 'Order dimension with order information';
COMMENT ON TABLE fact_sales IS 'Sales fact table containing sales transactions and measures';

-- ====================================================
-- END OF SCHEMA
-- ====================================================
