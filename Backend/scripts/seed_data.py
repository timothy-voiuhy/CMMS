#!/usr/bin/env python3
"""
Seed database with initial data for PSALMS Food Industries (SUMZ)
"""
import sys
import os
import json
from pathlib import Path

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from db.session import SessionLocal, engine
from db.base import Base
from models import (
    User, Company, Facility, Department, Craftsman, Skill,
    Equipment, InventoryItem, UserRole, EquipmentStatus, InventoryCategory,
    ProductionLine, ProductionLineEquipment, Shift, ProductionOrder, PackagingOrder,
    ProductionLineStatus, ShiftType, ProductionOrderStatus,
    QualityInspection, QualityInspectionItem, NonConformanceReport,
    InspectionStatus, InspectionResult, NCRStatus, NCRSeverity
)
from core.security import get_password_hash


def load_seed_data():
    """Load seed data from JSON file."""
    seed_file = Path(__file__).parent / "seed_data.json"
    with open(seed_file, 'r') as f:
        return json.load(f)


def seed_company(db: Session, data: dict):
    """Seed company data."""
    print("Creating company...")
    company = Company(**data)
    db.add(company)
    db.commit()
    db.refresh(company)
    print(f"✓ Created company: {company.name}")
    return company


def seed_facilities(db: Session, company_id: int, facilities_data: list):
    """Seed facilities data."""
    print("\nCreating facilities...")
    facilities = []
    for fac_data in facilities_data:
        fac_data['company_id'] = company_id
        facility = Facility(**fac_data)
        db.add(facility)
        db.commit()
        db.refresh(facility)
        facilities.append(facility)
        print(f"✓ Created facility: {facility.name}")
    return facilities


def seed_departments(db: Session, facility_id: int, departments_data: list):
    """Seed departments data."""
    print("\nCreating departments...")
    departments = []
    for dept_data in departments_data:
        dept_data['facility_id'] = facility_id
        department = Department(**dept_data)
        db.add(department)
        db.commit()
        db.refresh(department)
        departments.append(department)
        print(f"✓ Created department: {department.name}")
    return departments


def seed_users(db: Session, users_data: list):
    """Seed users data."""
    print("\nCreating users...")
    users = {}
    for user_data in users_data:
        password = user_data.pop('password')
        user = User(
            **user_data,
            hashed_password=get_password_hash(password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        users[user.username] = user
        print(f"✓ Created user: {user.username} ({user.role})")
    return users


def seed_skills(db: Session, skills_data: list):
    """Seed skills data."""
    print("\nCreating skills...")
    skills = {}
    for skill_data in skills_data:
        skill = Skill(**skill_data)
        db.add(skill)
        db.commit()
        db.refresh(skill)
        skills[skill.name] = skill
        print(f"✓ Created skill: {skill.name}")
    return skills


def seed_craftsmen(db: Session, users: dict, skills: dict, craftsmen_data: list):
    """Seed craftsmen data."""
    print("\nCreating craftsmen...")
    craftsmen = []
    for craft_data in craftsmen_data:
        username = craft_data.pop('user_username')
        skill_names = craft_data.pop('skills', [])
        
        user = users.get(username)
        if not user:
            print(f"✗ User {username} not found, skipping craftsman")
            continue
        
        craftsman = Craftsman(
            user_id=user.id,
            **craft_data
        )
        
        # Add skills
        for skill_name in skill_names:
            skill = skills.get(skill_name)
            if skill:
                craftsman.skills.append(skill)
        
        db.add(craftsman)
        db.commit()
        db.refresh(craftsman)
        craftsmen.append(craftsman)
        print(f"✓ Created craftsman: {user.full_name} with {len(skill_names)} skills")
    
    return craftsmen


def seed_equipment(db: Session, equipment_data: list):
    """Seed equipment data."""
    print("\nCreating equipment...")
    equipment_list = []
    for eq_data in equipment_data:
        # Convert status string to enum if needed
        if 'status' in eq_data:
            eq_data['status'] = EquipmentStatus[eq_data['status'].upper()]
        
        equipment = Equipment(**eq_data)
        db.add(equipment)
        db.commit()
        db.refresh(equipment)
        equipment_list.append(equipment)
        print(f"✓ Created equipment: {equipment.name} ({equipment.equipment_id})")
    
    return equipment_list


def seed_inventory_categories(db: Session, categories_data: list):
    """Seed inventory categories (hierarchical)."""
    print("\nCreating inventory categories...")
    category_map = {}
    
    for cat_data in categories_data:
        # Find parent if specified
        parent_id = None
        if cat_data.get("parent_name"):
            parent_category = category_map.get(cat_data["parent_name"])
            if parent_category:
                parent_id = parent_category.id
        
        category = InventoryCategory(
            name=cat_data["name"],
            description=cat_data.get("description"),
            parent_id=parent_id,
            is_active=cat_data.get("is_active", True)
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        category_map[category.name] = category  # Store the object to get ID later
        print(f"✓ Created category: {category.name}")
    
    return category_map


def seed_inventory(db: Session, categories: dict, inventory_data: list):
    """Seed inventory items."""
    print("\nCreating inventory items...")
    items = []
    for item_data in inventory_data:
        # Get category by name
        category_name = item_data.pop('category_name', None)
        category = categories.get(category_name) if category_name else None
        
        if not category:
            print(f"✗ Category '{category_name}' not found, skipping item {item_data.get('item_code')}")
            continue
        
        item = InventoryItem(
            **item_data,
            category_id=category.id
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        items.append(item)
        print(f"✓ Created inventory item: {item.name} ({item.item_code})")
    
    return items


def seed_production_lines(db: Session, production_lines_data: list):
    """Seed production lines."""
    print("\nCreating production lines...")
    lines = {}
    for line_data in production_lines_data:
        # Convert status string to enum if needed
        if 'status' in line_data:
            line_data['status'] = ProductionLineStatus[line_data['status'].upper()]
        
        line = ProductionLine(**line_data)
        db.add(line)
        db.commit()
        db.refresh(line)
        lines[line.line_code] = line
        print(f"✓ Created production line: {line.name} ({line.line_code})")
    
    return lines


def seed_production_line_equipment(db: Session, lines: dict, equipment_list: list, craftsmen: list, equipment_config: list):
    """Seed production line equipment stations."""
    print("\nConfiguring production line equipment...")
    stations = []
    
    # Create a lookup for equipment by name
    equipment_lookup = {eq.name: eq for eq in equipment_list}
    craftsmen_lookup = {c.employee_id: c for c in craftsmen}
    
    for config in equipment_config:
        line_code = config['line_code']
        line = lines.get(line_code)
        if not line:
            print(f"✗ Production line {line_code} not found, skipping equipment")
            continue
        
        equipment_name = config['equipment_name']
        equipment = equipment_lookup.get(equipment_name)
        if not equipment:
            print(f"✗ Equipment {equipment_name} not found, skipping")
            continue
        
        # Get operator IDs
        operator_ids = []
        for emp_id in config.get('operators', []):
            craftsman = craftsmen_lookup.get(emp_id)
            if craftsman:
                operator_ids.append(craftsman.id)
        
        station = ProductionLineEquipment(
            production_line_id=line.id,
            equipment_id=equipment.id,
            sequence_order=config['sequence_order'],
            station_name=config.get('station_name'),
            operators=operator_ids if operator_ids else None,
            cycle_time_minutes=config.get('cycle_time_minutes'),
            notes=config.get('notes')
        )
        
        db.add(station)
        db.commit()
        db.refresh(station)
        stations.append(station)
        print(f"✓ Added {equipment.name} to {line.name} (Station #{station.sequence_order})")
    
    return stations


def seed_shifts(db: Session, lines: dict, craftsmen: list, shifts_data: list):
    """Seed production shifts."""
    print("\nCreating production shifts...")
    shifts = []
    
    craftsmen_lookup = {c.employee_id: c for c in craftsmen}
    
    for shift_data in shifts_data:
        line_code = shift_data.pop('line_code')
        line = lines.get(line_code)
        if not line:
            print(f"✗ Production line {line_code} not found, skipping shift")
            continue
        
        # Convert shift_type to enum
        shift_data['shift_type'] = ShiftType[shift_data['shift_type'].upper()]
        
        # Get team leader ID
        team_leader_emp_id = shift_data.pop('team_leader_employee_id', None)
        if team_leader_emp_id:
            team_leader = craftsmen_lookup.get(team_leader_emp_id)
            shift_data['team_leader_id'] = team_leader.id if team_leader else None
        
        # Get operator IDs
        operator_emp_ids = shift_data.pop('operator_employee_ids', [])
        operator_ids = []
        for emp_id in operator_emp_ids:
            craftsman = craftsmen_lookup.get(emp_id)
            if craftsman:
                operator_ids.append(craftsman.id)
        shift_data['operators'] = operator_ids if operator_ids else None
        
        shift = Shift(
            production_line_id=line.id,
            **shift_data
        )
        
        db.add(shift)
        db.commit()
        db.refresh(shift)
        shifts.append(shift)
        print(f"✓ Created {shift.shift_type.value} shift for {line.name}")
    
    return shifts


def seed_production_orders(db: Session, lines: dict, orders_data: list):
    """Seed production orders."""
    print("\nCreating production orders...")
    orders = []
    
    for order_data in orders_data:
        line_code = order_data.pop('line_code')
        line = lines.get(line_code)
        if not line:
            print(f"✗ Production line {line_code} not found, skipping order")
            continue
        
        # Convert status to enum
        if 'status' in order_data:
            order_data['status'] = ProductionOrderStatus[order_data['status'].upper()]
        
        order = ProductionOrder(
            production_line_id=line.id,
            **order_data
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        orders.append(order)
        print(f"✓ Created production order: {order.order_number}")
    
    return orders


def main():
    """Main seeding function."""
    print("=" * 60)
    print("ICMS Database Seeding Script")
    print("Company: PSALMS Food Industries (SUMZ)")
    print("=" * 60)
    
    # Create tables
    print("\nCreating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    # Load seed data
    data = load_seed_data()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_company = db.query(Company).first()
        if existing_company:
            print("\n⚠ Database already contains data!")
            response = input("Do you want to clear and reseed? (yes/no): ")
            if response.lower() != 'yes':
                print("Seeding cancelled.")
                return
            
            print("\nClearing existing data...")
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            print("✓ Database cleared")
        
        # Seed data in order
        company = seed_company(db, data['company'])
        facilities = seed_facilities(db, company.id, data['facilities'])
        departments = seed_departments(db, facilities[0].id, data['departments'])
        users = seed_users(db, data['users'])
        skills = seed_skills(db, data['skills'])
        craftsmen = seed_craftsmen(db, users, skills, data['craftsmen'])
        equipment = seed_equipment(db, data['equipment'])
        
        # Seed inventory categories first, then items
        categories = seed_inventory_categories(db, data.get('inventory_categories', []))
        inventory = seed_inventory(db, categories, data['inventory_items'])
        
        # Seed production data if available
        production_lines = []
        equipment_stations = []
        shifts = []
        production_orders = []
        
        if 'production_lines' in data:
            production_lines = seed_production_lines(db, data['production_lines'])
            
            if 'production_line_equipment' in data:
                equipment_stations = seed_production_line_equipment(
                    db, production_lines, equipment, craftsmen, data['production_line_equipment']
                )
            
            if 'shifts' in data:
                shifts = seed_shifts(db, production_lines, craftsmen, data['shifts'])
            
            if 'production_orders' in data:
                production_orders = seed_production_orders(db, production_lines, data['production_orders'])
        
        # Seed quality data if available
        quality_inspections = []
        ncrs = []
        if 'quality_inspections' in data:
            quality_inspections = seed_quality_inspections(db, users, production_orders, data['quality_inspections'])
        
        if 'ncrs' in data:
            ncrs = seed_ncrs(db, users, quality_inspections, production_orders, equipment, data['ncrs'])
        
        print("\n" + "=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Company: 1")
        print(f"  - Facilities: {len(facilities)}")
        print(f"  - Departments: {len(departments)}")
        print(f"  - Users: {len(users)}")
        print(f"  - Skills: {len(skills)}")
        print(f"  - Craftsmen: {len(craftsmen)}")
        print(f"  - Equipment: {len(equipment)}")
        print(f"  - Inventory Categories: {len(categories)}")
        print(f"  - Inventory Items: {len(inventory)}")
        if production_lines:
            print(f"  - Production Lines: {len(production_lines)}")
            print(f"  - Equipment Stations: {len(equipment_stations)}")
            print(f"  - Shifts: {len(shifts)}")
            print(f"  - Production Orders: {len(production_orders)}")
        if quality_inspections:
            print(f"  - Quality Inspections: {len(quality_inspections)}")
            print(f"  - Non-Conformance Reports: {len(ncrs)}")
        print("\nDefault login credentials:")
        print("  Username: admin")
        print("  Password: Admin@123")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()


def seed_quality_inspections(db: Session, users: list, production_orders: list, inspections_data: list):
    """Seed quality inspections."""
    print("\nCreating quality inspections...")
    inspections = []
    
    # Get first admin user as inspector
    inspector = next((u for u in users if u.role == UserRole.ADMIN), users[0])
    
    inspection_num = 1
    for insp_data in inspections_data:
        items_data = insp_data.pop('inspection_items', [])
        
        # Set inspector
        insp_data['inspector_id'] = inspector.id
        
        # Generate inspection number
        insp_data['inspection_number'] = f"QI-{inspection_num:06d}"
        inspection_num += 1
        
        # Link to production order if batch_number matches
        if 'batch_number' in insp_data and production_orders:
            for order in production_orders:
                insp_data['production_order_id'] = order.id
                break
        
        inspection = QualityInspection(**insp_data)
        db.add(inspection)
        db.flush()
        
        # Add inspection items
        for item_data in items_data:
            item_data['inspection_id'] = inspection.id
            item = QualityInspectionItem(**item_data)
            db.add(item)
        
        inspections.append(inspection)
    
    db.commit()
    for inspection in inspections:
        db.refresh(inspection)
    print(f"✓ Created {len(inspections)} quality inspections")
    return inspections


def seed_ncrs(db: Session, users: list, quality_inspections: list, production_orders: list, equipment: list, ncrs_data: list):
    """Seed non-conformance reports."""
    print("\nCreating non-conformance reports...")
    ncrs = []
    
    # Get users for reporting and assignment
    reporter = next((u for u in users if u.role == UserRole.ADMIN), users[0])
    assigned_to = next((u for u in users if u.username != reporter.username), users[0])
    
    ncr_num = 1
    for ncr_data in ncrs_data:
        # Generate NCR number
        ncr_data['ncr_number'] = f"NCR-{ncr_num:06d}"
        ncr_num += 1
        
        # Set reporter and assignee
        ncr_data['reported_by_id'] = reporter.id
        ncr_data['assigned_to_id'] = assigned_to.id
        
        # Link to inspection if batch matches
        if 'batch_number' in ncr_data and quality_inspections:
            batch = ncr_data['batch_number']
            matching_insp = next((i for i in quality_inspections if i.batch_number == batch), None)
            if matching_insp:
                ncr_data['inspection_id'] = matching_insp.id
                ncr_data['production_order_id'] = matching_insp.production_order_id
        
        # Link to equipment if mentioned
        if equipment and ncr_data.get('title', '').lower().find('fryer') >= 0:
            fryer = next((e for e in equipment if 'fryer' in e.name.lower()), None)
            if fryer:
                ncr_data['equipment_id'] = fryer.id
        
        ncr = NonConformanceReport(**ncr_data)
        db.add(ncr)
        ncrs.append(ncr)
    
    db.commit()
    for ncr in ncrs:
        db.refresh(ncr)
    print(f"✓ Created {len(ncrs)} non-conformance reports")
    return ncrs
