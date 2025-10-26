-- Supabase Produce Table Schema

CREATE TABLE produce (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farmer_id TEXT NOT NULL,
    produce_name TEXT NOT NULL,
    weight DECIMAL(10, 2) NOT NULL,
    unit TEXT NOT NULL,
    weight_confidence DECIMAL(3, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    creao_logged BOOLEAN DEFAULT FALSE
);

-- Add indexes for faster queries
CREATE INDEX idx_produce_farmer_id ON produce(farmer_id);
CREATE INDEX idx_produce_created_at ON produce(created_at DESC);
