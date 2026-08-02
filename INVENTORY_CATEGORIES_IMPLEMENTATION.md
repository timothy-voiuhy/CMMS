# Inventory Categories Implementation

## Overview
Implemented hierarchical inventory categories to replace the flat enum-based system. This allows users to organize inventory items in a tree structure (e.g., Flavors → BBQ Flavor, Salt & Vinegar).

## Changes Made

### Backend Changes

#### 1. Database Models (`Backend/models/inventory.py`)
- **Replaced** `InventoryCategory` enum with a new `InventoryCategory` model table
- **New Table**: `inventory_categories`
  - `id`: Primary key
  - `name`: Category name
  - `description`: Optional description
  - `parent_id`: Self-referential foreign key for hierarchy
  - `is_active`: Boolean flag for soft deletes
  - `parent`: Relationship to parent category
  - `children`: Relationship to child categories
  - `items`: Relationship to inventory items

- **Updated** `InventoryItem` model:
  - Changed `category` (enum field) → `category_id` (foreign key to `inventory_categories`)
  - Added `category` relationship to `InventoryCategory`

#### 2. Schemas (`Backend/schemas/inventory.py`)
- **Added Category Schemas**:
  - `InventoryCategoryBase`: Base fields
  - `InventoryCategoryCreate`: Create request
  - `InventoryCategoryUpdate`: Update request (all fields optional)
  - `InventoryCategoryResponse`: Response with timestamps
  - `InventoryCategoryTree`: Response with nested children for tree view

- **Updated Item Schemas**:
  - Changed `category: InventoryCategory` → `category_id: int`
  - Added `InventoryItemWithCategory`: Includes full category details

#### 3. Services (`Backend/services/inventory_service.py`)
- **Added Category Service Functions**:
  - `get_categories(db, include_inactive)`: Get flat list of categories
  - `get_category_tree(db)`: Get root categories with children
  - `get_category(db, category_id)`: Get single category
  - `create_category(db, category)`: Create new category (validates parent exists)
  - `update_category(db, category_id, category)`: Update category (prevents circular references)
  - `delete_category(db, category_id)`: Smart delete (soft delete if has dependencies, hard delete otherwise)

- **Updated Item Service Functions**:
  - Updated filters to use `category_id` instead of enum
  - Added `joinedload(InventoryItem.category)` for eager loading
  - Updated statistics to use actual category names from database

#### 4. API Endpoints (`Backend/api/v1/inventory.py`)
- **Added Category Endpoints**:
  - `GET /inventory/categories`: List all categories (flat)
  - `GET /inventory/categories/tree`: Get category tree structure
  - `POST /inventory/categories`: Create category
  - `GET /inventory/categories/{id}`: Get single category
  - `PUT /inventory/categories/{id}`: Update category
  - `DELETE /inventory/categories/{id}`: Delete category

- **Updated Item Endpoints**:
  - Changed `category` filter parameter → `category_id`
  - Updated response models to include category details

#### 5. Database Migration (`Backend/db/migrations/versions/b1cde3f4a5b6_add_inventory_categories.py`)
- Creates `inventory_categories` table
- Adds `category_id` column to `inventory_items`
- Migrates existing enum data to new categories (creates 7 default categories)
- Drops old `category` enum column
- Includes downgrade path for rollback

#### 6. Seed Data Updates

**`Backend/scripts/seed_data.py`**:
- Added `seed_inventory_categories()` function
  - Handles hierarchical seeding (parent categories first)
  - Returns category map for item seeding
- Updated `seed_inventory()` function
  - Takes category map parameter
  - Maps `category_name` to `category_id`
- Updated import to include `InventoryCategory` model

**`Backend/scripts/seed_data.json`**:
- **Added** `inventory_categories` section with hierarchical structure:
  - **Root Categories**: Raw Materials, Flavors & Seasonings, Packaging Materials, Spare Parts, Finished Goods, Work in Progress
  - **Child Categories**:
    - Under Raw Materials: Potatoes, Grains, Oils & Fats
    - Under Flavors & Seasonings: BBQ Flavor, Salt & Vinegar, Original/Plain, Cheese Flavor
    - Under Packaging Materials: Bags & Pouches, Cartons & Boxes, Labels & Stickers

- **Updated** `inventory_items` section:
  - Changed `category` (enum string) → `category_name` (string reference)
  - Added new flavor items (BBQ, Salt & Vinegar, Plain Salt)
  - Updated existing items to use specific category names

### Frontend Changes

#### 1. Service Layer (`icms-web/src/services/inventory.service.ts`)
- **Added Category Types**:
  - `InventoryCategory`: Category object with all fields
  - `InventoryCategoryTree`: Category with nested children
  - `CreateInventoryCategoryRequest`: Create request
  - `UpdateInventoryCategoryRequest`: Update request

- **Added Category Methods**:
  - `getCategories(includeInactive)`: Get flat category list
  - `getCategoryTree()`: Get tree structure
  - `getCategoryById(id)`: Get single category
  - `createCategory(data)`: Create category
  - `updateCategory(id, data)`: Update category
  - `deleteCategory(id)`: Delete category

- **Updated Item Types & Methods**:
  - Changed `category: InventoryCategory` (enum) → `category_id: number`
  - Added optional `category?: InventoryCategory` to `InventoryItem`
  - Updated filters: `category` → `category_id`

#### 2. Category Management Page (`icms-web/src/pages/inventory/InventoryCategoriesPage.tsx`)
- **New page** for managing categories
- **Features**:
  - Tree view with visual hierarchy (indented levels)
  - Create/Edit/Delete operations
  - Parent category selection
  - Active/Inactive toggle
  - Visual indicators for inactive categories
  - Confirmation dialogs for deletion

#### 3. Inventory Form Page (`icms-web/src/pages/inventory/InventoryFormPage.tsx`)
- **Updated category selector**:
  - Loads categories on mount
  - Dropdown shows hierarchical structure with indentation
  - Uses `renderCategoryOptions()` recursive function
  - Changed from enum strings to category IDs

#### 4. Inventory List Page (`icms-web/src/pages/inventory/InventoryListPage.tsx`)
- **Updated category display**:
  - Shows `item.category?.name` instead of formatted enum
  - Displays "Uncategorized" for missing categories
- **Updated category filter**:
  - Loads categories from API
  - Dropdown populated dynamically
  - Uses category IDs instead of enum values
- **Added "Manage Categories" button** to navigate to category management

#### 5. Routing (`icms-web/src/App.tsx`)
- Added route: `/inventory/categories` → `InventoryCategoriesPage`
- Route placed before `/inventory/:id` to avoid conflicts

## Database Schema

### inventory_categories Table
```sql
CREATE TABLE inventory_categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    parent_id INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES inventory_categories(id)
);
```

### inventory_items Table (Updated)
```sql
-- Removed: category VARCHAR(50) NOT NULL
-- Added:
category_id INTEGER NOT NULL,
FOREIGN KEY (category_id) REFERENCES inventory_categories(id)
```

## Sample Category Hierarchy

```
Raw Materials
├── Potatoes
├── Grains
└── Oils & Fats

Flavors & Seasonings
├── BBQ Flavor
├── Salt & Vinegar
├── Original/Plain
└── Cheese Flavor

Packaging Materials
├── Bags & Pouches
├── Cartons & Boxes
└── Labels & Stickers

Spare Parts
Finished Goods
Work in Progress
```

## API Endpoints

### Category Endpoints
- `GET /api/v1/inventory/categories` - List all categories
- `GET /api/v1/inventory/categories/tree` - Get tree structure
- `POST /api/v1/inventory/categories` - Create category
- `GET /api/v1/inventory/categories/{id}` - Get category
- `PUT /api/v1/inventory/categories/{id}` - Update category
- `DELETE /api/v1/inventory/categories/{id}` - Delete category

### Updated Item Endpoints
- `GET /api/v1/inventory/?category_id={id}` - Filter by category ID
- Response includes full category details in item objects

## Migration Instructions

### Option 1: Fresh Installation (Recommended)

If you don't have important data, the easiest approach is to reseed:

```bash
cd Backend

# Reset the inventory schema
sqlite3 icms.db < scripts/reset_inventory_schema.sql

# Reseed with hierarchical categories
python scripts/seed_data.py
```

This will give you the full hierarchical category structure defined in `seed_data.json`.

### Option 2: Existing Database with Data

If you have existing inventory data you want to keep:

1. **Manually create categories** via the UI or API after migration
2. **Update existing items** to reference the new categories

The migration creates temporary default categories only if there are existing items.

### For Completely New Databases

Simply run:
```bash
cd Backend
python scripts/seed_data.py
```

Categories will be created from `seed_data.json` with the full hierarchy.

## Important: Categories are User-Configurable

Unlike the previous enum-based system, **categories are now fully user-configurable**:
- Users create their own category hierarchy through the UI (`/inventory/categories`)
- No hardcoded categories in production
- The `seed_data.json` file contains **sample** categories for demonstration
- Each organization can define categories that match their business needs

## Features

### Smart Category Deletion
- **If category has items or children**: Soft delete (sets `is_active=False`)
- **If category is empty**: Hard delete (removes from database)

### Parent-Child Validation
- Cannot set category as its own parent
- Parent must exist when specified
- Prevents circular references

### Frontend UX
- Hierarchical dropdown with visual indentation
- Tree view in category management
- Inactive categories grayed out
- Confirmation before deletion
- Real-time category loading

## Testing Checklist

- [ ] Run migration successfully
- [ ] Seed data creates hierarchical categories
- [ ] Category management page loads
- [ ] Create root category
- [ ] Create child category
- [ ] Edit category (change name, parent, active status)
- [ ] Delete empty category (hard delete)
- [ ] Delete category with items (soft delete)
- [ ] Inventory form shows hierarchical categories
- [ ] Create inventory item with category
- [ ] Edit inventory item category
- [ ] Filter inventory by category
- [ ] Statistics show category-based counts

## Future Enhancements
- Drag-and-drop category reordering
- Category icons/colors
- Category-based permissions
- Bulk category assignment for items
- Category export/import
- Category usage analytics
