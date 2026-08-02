-- Script to manually fix the inventory schema
-- Run this if the migration partially completed

-- First, check current state
SELECT 'Current inventory_items columns:' as info;
PRAGMA table_info(inventory_items);

SELECT 'Current inventory_categories count:' as info;
SELECT COUNT(*) FROM inventory_categories;

-- Drop and recreate inventory_items table with correct schema
DROP TABLE IF EXISTS inventory_items;

CREATE TABLE inventory_items (
    id INTEGER NOT NULL,
    item_code VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL,
    quantity FLOAT NOT NULL DEFAULT 0.0,
    min_quantity FLOAT,
    max_quantity FLOAT,
    reorder_point FLOAT,
    unit_cost FLOAT,
    location VARCHAR(200),
    supplier VARCHAR(200),
    notes TEXT,
    batch_number VARCHAR(100),
    expiry_date VARCHAR(20),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY(category_id) REFERENCES inventory_categories (id)
);

CREATE INDEX ix_inventory_items_item_code ON inventory_items (item_code);

-- Clear any temporary migration categories
DELETE FROM inventory_categories;

SELECT 'Schema fixed. Now run: python scripts/seed_data.py' as next_step;
