-- Supabase Product Table Schema

CREATE TABLE Product (
    id VARCHAR(255) PRIMARY KEY,
    seller_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(255) NOT NULL,
    price NUMERIC NOT NULL,
    unit VARCHAR(50) NOT NULL,
    stock_quantity INTEGER NOT NULL,
    image_url VARCHAR(2048),
    available BOOLEAN NOT NULL,
    data_creator VARCHAR(255) NOT NULL,
    data_updater VARCHAR(255) NOT NULL,
    create_time TIMESTAMP WITH TIME ZONE NOT NULL,
    update_time TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Add indexes for faster queries
CREATE INDEX idx_product_seller_id ON Product(seller_id);
CREATE INDEX idx_product_create_time ON Product(create_time DESC);
